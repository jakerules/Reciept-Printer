/**
 * Main JavaScript for Email Task Manager
 */

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize task status updates
    initTaskStatusUpdates();
    
    // Initialize task assignment
    initTaskAssignment();
    
    // Initialize batch selection
    initBatchSelection();
    
    // Initialize date pickers
    initDatePickers();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize task status updates via AJAX
 */
function initTaskStatusUpdates() {
    const statusForms = document.querySelectorAll('.task-status-form');
    
    statusForms.forEach(form => {
        const statusSelect = form.querySelector('select[name="status"]');
        
        if (statusSelect) {
            statusSelect.addEventListener('change', function() {
                // Submit the form via AJAX
                const formData = new FormData(form);
                const taskId = form.getAttribute('data-task-id');
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success message
                        showAlert('Task status updated successfully', 'success');
                        
                        // Update UI if needed
                        const statusBadge = document.querySelector(`.task-status-badge-${taskId}`);
                        if (statusBadge) {
                            // Remove old status classes
                            statusBadge.classList.remove('task-status-new', 'task-status-in-progress', 'task-status-completed', 'task-status-cancelled');
                            
                            // Add new status class
                            statusBadge.classList.add(`task-status-${statusSelect.value.toLowerCase().replace(' ', '-')}`);
                            
                            // Update text
                            statusBadge.textContent = statusSelect.value;
                        }
                    } else {
                        showAlert('Failed to update task status', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred while updating task status', 'error');
                });
            });
        }
    });
}

/**
 * Initialize task assignment via AJAX
 */
function initTaskAssignment() {
    const assignForms = document.querySelectorAll('.task-assign-form');
    
    assignForms.forEach(form => {
        const userSelect = form.querySelector('select[name="user_id"]');
        
        if (userSelect) {
            userSelect.addEventListener('change', function() {
                form.submit();
            });
        }
    });
}

/**
 * Initialize batch selection for tasks
 */
function initBatchSelection() {
    const selectAllCheckbox = document.getElementById('select-all-tasks');
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    const batchActionButtons = document.querySelectorAll('.batch-action');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            
            // Update all task checkboxes
            taskCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            
            // Update batch action buttons
            updateBatchActionButtons();
        });
    }
    
    // Add event listeners to individual checkboxes
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateBatchActionButtons();
            
            // Update "select all" checkbox
            if (selectAllCheckbox) {
                const allChecked = Array.from(taskCheckboxes).every(cb => cb.checked);
                const someChecked = Array.from(taskCheckboxes).some(cb => cb.checked);
                
                selectAllCheckbox.checked = allChecked;
                selectAllCheckbox.indeterminate = someChecked && !allChecked;
            }
        });
    });
    
    // Function to update batch action buttons
    function updateBatchActionButtons() {
        const checkedCount = document.querySelectorAll('.task-checkbox:checked').length;
        
        batchActionButtons.forEach(button => {
            button.disabled = checkedCount === 0;
            
            // Update count in button text if it has a counter
            const counter = button.querySelector('.selected-count');
            if (counter) {
                counter.textContent = checkedCount;
            }
        });
    }
    
    // Initialize batch action buttons state
    updateBatchActionButtons();
}

/**
 * Initialize date pickers
 */
function initDatePickers() {
    const datePickers = document.querySelectorAll('.datepicker');
    
    datePickers.forEach(input => {
        // This assumes you're using the browser's native datetime-local input
        // If you want to use a library like flatpickr or bootstrap-datepicker,
        // you would initialize it here
    });
}

/**
 * Show an alert message
 * 
 * @param {string} message - The message to display
 * @param {string} type - The type of alert (success, error, info, warning)
 */
function showAlert(message, type = 'info') {
    // Map type to Bootstrap alert class
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'info': 'alert-info',
        'warning': 'alert-warning'
    }[type] || 'alert-info';
    
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert ${alertClass} alert-dismissible fade show`;
    alertElement.role = 'alert';
    
    // Add message
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to container
    const container = document.querySelector('.container');
    container.insertBefore(alertElement, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertElement);
        bsAlert.close();
    }, 5000);
}