/**
 * Southern Lee Wrestling - Custom JavaScript
 * Enhanced functionality for wrestling roster management
 */

// Initialize when page loads
document.addEventListener("DOMContentLoaded", function () {
  initializeWrestlingFeatures();
});

function initializeWrestlingFeatures() {
  // Enhanced form validation
  setupFormValidation();

  // Dynamic weight class filtering
  setupWeightClassFiltering();

  // Enhanced table features
  setupTableEnhancements();

  // Auto-dismiss flash messages
  setupFlashMessages();

  // Confirmation dialogs
  setupConfirmationDialogs();
}

/**
 * Enhanced Form Validation
 */
function setupFormValidation() {
  const forms = document.querySelectorAll('form[data-validate="true"]');

  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      if (!validateForm(this)) {
        e.preventDefault();
        showFormErrors();
      }
    });
  });
}

function validateForm(form) {
  let isValid = true;
  const requiredFields = form.querySelectorAll("[required]");

  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      field.classList.add("is-invalid");
      isValid = false;
    } else {
      field.classList.remove("is-invalid");
    }
  });

  return isValid;
}

function showFormErrors() {
  const invalidFields = document.querySelectorAll(".is-invalid");
  if (invalidFields.length > 0) {
    invalidFields[0].focus();
    showToast("Please fill in all required fields", "error");
  }
}

/**
 * Dynamic Weight Class Filtering
 */
function setupWeightClassFiltering() {
  const divisionSelect = document.getElementById("division");
  const weightClassSelect = document.getElementById("weight_class_id");

  if (divisionSelect && weightClassSelect) {
    divisionSelect.addEventListener("change", function () {
      filterWeightClasses(this.value, weightClassSelect);
    });

    // Initial filter on page load
    if (divisionSelect.value) {
      filterWeightClasses(divisionSelect.value, weightClassSelect);
    }
  }
}

function filterWeightClasses(selectedDivision, weightClassSelect) {
  const options = weightClassSelect.querySelectorAll("option");
  let hasVisibleOptions = false;

  options.forEach((option) => {
    if (option.value === "") {
      option.style.display = "block";
      option.textContent = selectedDivision
        ? "Select Weight Class"
        : "First select a division";
    } else {
      const optionDivision = option.getAttribute("data-division");
      const shouldShow = optionDivision === selectedDivision;
      option.style.display = shouldShow ? "block" : "none";

      if (shouldShow) hasVisibleOptions = true;
    }
  });

  // Reset selection and update placeholder
  weightClassSelect.value = "";

  if (!hasVisibleOptions && selectedDivision) {
    const noOptionsMsg = document.createElement("option");
    noOptionsMsg.value = "";
    noOptionsMsg.textContent = "No weight classes available for this division";
    noOptionsMsg.disabled = true;
    weightClassSelect.appendChild(noOptionsMsg);
  }

  // Show count of available weight classes
  updateWeightClassCount(selectedDivision, options);
}

function updateWeightClassCount(division, options) {
  const countElement = document.getElementById("weight-class-count");
  if (countElement && division) {
    const count = Array.from(options).filter(
      (option) =>
        option.getAttribute("data-division") === division && option.value !== ""
    ).length;

    countElement.textContent = `${count} weight classes available`;
    countElement.style.display = "block";
  } else if (countElement) {
    countElement.style.display = "none";
  }
}

/**
 * Enhanced Table Features
 */
function setupTableEnhancements() {
  // Add search functionality to tables
  const searchInputs = document.querySelectorAll(".table-search");
  searchInputs.forEach((input) => {
    input.addEventListener("keyup", function () {
      searchTable(this.value, this.getAttribute("data-target"));
    });
  });

  // Add sort functionality
  const sortHeaders = document.querySelectorAll(".sortable");
  sortHeaders.forEach((header) => {
    header.addEventListener("click", function () {
      sortTable(this);
    });
    header.style.cursor = "pointer";
    header.title = "Click to sort";
  });
}

function searchTable(searchTerm, tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const rows = table.querySelectorAll("tbody tr");
  const term = searchTerm.toLowerCase();

  rows.forEach((row) => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(term) ? "" : "none";
  });
}

function sortTable(header) {
  const table = header.closest("table");
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const columnIndex = Array.from(header.parentNode.children).indexOf(header);

  const isAscending = !header.classList.contains("sort-asc");

  // Remove existing sort classes
  header.parentNode.querySelectorAll("th").forEach((th) => {
    th.classList.remove("sort-asc", "sort-desc");
  });

  // Add new sort class
  header.classList.add(isAscending ? "sort-asc" : "sort-desc");

  rows.sort((a, b) => {
    const aValue = a.children[columnIndex].textContent.trim();
    const bValue = b.children[columnIndex].textContent.trim();

    // Try to parse as numbers
    const aNum = parseFloat(aValue);
    const bNum = parseFloat(bValue);

    if (!isNaN(aNum) && !isNaN(bNum)) {
      return isAscending ? aNum - bNum : bNum - aNum;
    }

    // String comparison
    return isAscending
      ? aValue.localeCompare(bValue)
      : bValue.localeCompare(aValue);
  });

  rows.forEach((row) => tbody.appendChild(row));
}

/**
 * Flash Messages
 */
function setupFlashMessages() {
  const flashMessages = document.querySelectorAll(".alert");

  flashMessages.forEach((message) => {
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      if (message.parentNode) {
        message.style.opacity = "0";
        setTimeout(() => {
          if (message.parentNode) {
            message.remove();
          }
        }, 300);
      }
    }, 5000);

    // Add close button if not present
    if (!message.querySelector(".btn-close")) {
      const closeBtn = document.createElement("button");
      closeBtn.type = "button";
      closeBtn.className = "btn-close";
      closeBtn.setAttribute("aria-label", "Close");
      closeBtn.onclick = () => message.remove();
      message.appendChild(closeBtn);
    }
  });
}

/**
 * Confirmation Dialogs
 */
function setupConfirmationDialogs() {
  const deleteButtons = document.querySelectorAll("[data-confirm]");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      const message = this.getAttribute("data-confirm") || "Are you sure?";
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });
}

/**
 * Utility Functions
 */
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `alert alert-${type} toast-message`;
  toast.textContent = message;
  toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideOutRight 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function showLoading(element) {
  const originalContent = element.innerHTML;
  element.innerHTML = '<span class="spinner-sl"></span> Loading...';
  element.disabled = true;

  return () => {
    element.innerHTML = originalContent;
    element.disabled = false;
  };
}

// Add CSS animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .sortable::after {
        content: ' ↕️';
        font-size: 0.8em;
        opacity: 0.5;
    }
    
    .sort-asc::after {
        content: ' ↑';
        opacity: 1;
    }
    
    .sort-desc::after {
        content: ' ↓';
        opacity: 1;
    }
    
    .is-invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    }
    
    .toast-message {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
`;
document.head.appendChild(style);
