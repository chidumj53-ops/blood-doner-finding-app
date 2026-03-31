const donorGrid = document.getElementById("donorGrid");
const resultCount = document.getElementById("resultCount");

const searchInput = document.getElementById("searchInput");
const bloodGroupFilter = document.getElementById("bloodGroupFilter");
const cityFilter = document.getElementById("cityFilter");
const availabilityFilter = document.getElementById("availabilityFilter");
const sortFilter = document.getElementById("sortFilter");
const refreshBtn = document.getElementById("refreshBtn");

const donorForm = document.getElementById("donorForm");
const formMessage = document.getElementById("formMessage");

const adminLoginBtn = document.getElementById("adminLoginBtn");
const adminLogoutBtn = document.getElementById("adminLogoutBtn");
const adminMessage = document.getElementById("adminMessage");
const adminLoginBox = document.getElementById("adminLoginBox");
const adminLoggedInBox = document.getElementById("adminLoggedInBox");

const editModal = document.getElementById("editModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const editDonorForm = document.getElementById("editDonorForm");

let isAdmin = false;
let debounceTimer = null;


async function fetchCities() {
    try {
        const res = await fetch("/api/meta/cities");
        const data = await res.json();

        cityFilter.innerHTML = `<option value="">All Cities</option>`;
        data.cities.forEach(city => {
            cityFilter.innerHTML += `<option value="${city}">${city}</option>`;
        });
    } catch (error) {
        console.error("Failed to load cities:", error);
    }
}


async function checkAdmin() {
    try {
        const res = await fetch("/api/admin/check");
        const data = await res.json();
        isAdmin = data.is_admin;
        updateAdminUI();
    } catch (error) {
        console.error("Admin check failed:", error);
    }
}


function updateAdminUI() {
    if (isAdmin) {
        adminLoginBox.classList.add("hidden");
        adminLoggedInBox.classList.remove("hidden");
    } else {
        adminLoginBox.classList.remove("hidden");
        adminLoggedInBox.classList.add("hidden");
    }
}


function buildQueryParams() {
    const params = new URLSearchParams();

    if (searchInput.value.trim()) {
        params.append("search", searchInput.value.trim());
    }

    if (bloodGroupFilter.value) {
        params.append("blood_group", bloodGroupFilter.value);
    }

    if (cityFilter.value) {
        params.append("city", cityFilter.value);
    }

    if (availabilityFilter.value) {
        params.append("available", availabilityFilter.value);
    }

    if (sortFilter.value) {
        params.append("sort_by", sortFilter.value);
    }

    return params.toString();
}


async function loadDonors() {
    try {
        donorGrid.innerHTML = `<div class="empty-state">Loading donors...</div>`;

        const query = buildQueryParams();
        const res = await fetch(`/api/donors?${query}`);
        const data = await res.json();

        renderDonors(data.donors || []);
        resultCount.textContent = `${data.count || 0} donor(s) found`;
    } catch (error) {
        donorGrid.innerHTML = `<div class="empty-state">Failed to load donors.</div>`;
        console.error("Failed to load donors:", error);
    }
}


function renderDonors(donors) {
    if (!donors.length) {
        donorGrid.innerHTML = `
            <div class="empty-state">
                <h3>No donors found</h3>
                <p>Try changing blood group, city, or search text.</p>
            </div>
        `;
        return;
    }

    donorGrid.innerHTML = donors.map(donor => `
        <div class="donor-card">
            <div class="donor-top">
                <div>
                    <div class="donor-name">${donor.full_name}</div>
                    <div>${donor.city}${donor.area ? ", " + donor.area : ""}</div>
                </div>
                <div class="blood-badge">${donor.blood_group}</div>
            </div>

            <div class="status-badge ${donor.available ? "success" : "offline"}">
                ${donor.available ? "Available Now" : "Currently Unavailable"}
            </div>

            <div class="donor-meta">
                <div><strong>Age:</strong> ${donor.age}</div>
                <div><strong>Gender:</strong> ${donor.gender || "-"}</div>
                <div><strong>Last Donated:</strong> ${donor.last_donated || "-"}</div>
            </div>

            <div class="contact-links">
                <a href="tel:${donor.phone}">📞 ${donor.phone}</a>
                <a href="mailto:${donor.email}">✉️ ${donor.email}</a>
            </div>

            ${isAdmin ? `
                <div class="card-actions">
                    <button class="small-btn edit-btn" onclick='openEditModal(${JSON.stringify(donor)})'>Edit</button>
                    <button class="small-btn delete-btn" onclick='deleteDonor(${donor.id})'>Delete</button>
                </div>
            ` : ""}
        </div>
    `).join("");
}


function showMessage(element, message, isError = false) {
    element.textContent = message;
    element.style.color = isError ? "#fecaca" : "#86efac";

    setTimeout(() => {
        element.textContent = "";
    }, 4000);
}


donorForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const donorData = {
        full_name: document.getElementById("full_name").value.trim(),
        blood_group: document.getElementById("blood_group").value,
        city: document.getElementById("city").value.trim(),
        area: document.getElementById("area").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        email: document.getElementById("email").value.trim(),
        age: parseInt(document.getElementById("age").value),
        gender: document.getElementById("gender").value,
        last_donated: document.getElementById("last_donated").value,
        available: document.getElementById("available").checked
    };

    try {
        const res = await fetch("/api/donors", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(donorData)
        });

        const data = await res.json();

        if (!res.ok) {
            showMessage(formMessage, data.message || "Failed to register donor", true);
            return;
        }

        donorForm.reset();
        document.getElementById("available").checked = true;
        showMessage(formMessage, data.message || "Donor registered successfully");
        await fetchCities();
        await loadDonors();
    } catch (error) {
        console.error(error);
        showMessage(formMessage, "Something went wrong while registering donor", true);
    }
});


adminLoginBtn.addEventListener("click", async () => {
    const username = document.getElementById("adminUsername").value.trim();
    const password = document.getElementById("adminPassword").value.trim();

    try {
        const res = await fetch("/api/admin/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (!res.ok) {
            showMessage(adminMessage, data.message || "Login failed", true);
            return;
        }

        isAdmin = true;
        updateAdminUI();
        showMessage(adminMessage, data.message || "Admin login successful");
        loadDonors();
    } catch (error) {
        console.error(error);
        showMessage(adminMessage, "Admin login failed", true);
    }
});


adminLogoutBtn.addEventListener("click", async () => {
    try {
        await fetch("/api/admin/logout", {
            method: "POST"
        });

        isAdmin = false;
        updateAdminUI();
        showMessage(adminMessage, "Logged out successfully");
        loadDonors();
    } catch (error) {
        console.error(error);
        showMessage(adminMessage, "Logout failed", true);
    }
});


window.openEditModal = function (donor) {
    document.getElementById("edit_id").value = donor.id;
    document.getElementById("edit_full_name").value = donor.full_name;
    document.getElementById("edit_blood_group").value = donor.blood_group;
    document.getElementById("edit_city").value = donor.city;
    document.getElementById("edit_area").value = donor.area || "";
    document.getElementById("edit_phone").value = donor.phone;
    document.getElementById("edit_email").value = donor.email;
    document.getElementById("edit_age").value = donor.age;
    document.getElementById("edit_gender").value = donor.gender || "";
    document.getElementById("edit_last_donated").value = donor.last_donated || "";
    document.getElementById("edit_available").checked = donor.available;

    editModal.classList.remove("hidden");
};


closeModalBtn.addEventListener("click", () => {
    editModal.classList.add("hidden");
});


editDonorForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const donorId = document.getElementById("edit_id").value;

    const updatedData = {
        full_name: document.getElementById("edit_full_name").value.trim(),
        blood_group: document.getElementById("edit_blood_group").value,
        city: document.getElementById("edit_city").value.trim(),
        area: document.getElementById("edit_area").value.trim(),
        phone: document.getElementById("edit_phone").value.trim(),
        email: document.getElementById("edit_email").value.trim(),
        age: parseInt(document.getElementById("edit_age").value),
        gender: document.getElementById("edit_gender").value,
        last_donated: document.getElementById("edit_last_donated").value,
        available: document.getElementById("edit_available").checked
    };

    try {
        const res = await fetch(`/api/donors/${donorId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(updatedData)
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.message || "Update failed");
            return;
        }

        editModal.classList.add("hidden");
        loadDonors();
    } catch (error) {
        console.error(error);
        alert("Failed to update donor");
    }
});


window.deleteDonor = async function (donorId) {
    const confirmDelete = confirm("Are you sure you want to delete this donor?");
    if (!confirmDelete) return;

    try {
        const res = await fetch(`/api/donors/${donorId}`, {
            method: "DELETE"
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.message || "Delete failed");
            return;
        }

        loadDonors();
    } catch (error) {
        console.error(error);
        alert("Failed to delete donor");
    }
};


function setupLiveFilters() {
    [bloodGroupFilter, cityFilter, availabilityFilter, sortFilter].forEach(element => {
        element.addEventListener("change", loadDonors);
    });

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(loadDonors, 250);
    });

    refreshBtn.addEventListener("click", loadDonors);
}


window.addEventListener("click", (e) => {
    if (e.target === editModal) {
        editModal.classList.add("hidden");
    }
});


async function init() {
    await fetchCities();
    await checkAdmin();
    setupLiveFilters();
    await loadDonors();
}

init();