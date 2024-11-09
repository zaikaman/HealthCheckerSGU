document.addEventListener('DOMContentLoaded', function() {
    // Edit Reminder functionality
    function initializeEditReminders() {
        document.querySelectorAll('.edit-reminder').forEach(button => {
            button.addEventListener('click', function() {
                const reminderId = this.dataset.reminderId;
                const modal = new bootstrap.Modal(document.getElementById('editReminderModal'));
                
                // Populate form fields
                document.getElementById('editReminderId').value = reminderId;
                document.getElementById('editTitle').value = this.dataset.title;
                document.getElementById('editDescription').value = this.dataset.description;
                document.getElementById('editType').value = this.dataset.type;
                document.getElementById('editFrequency').value = this.dataset.frequency;
                document.getElementById('editTime').value = this.dataset.time;
                document.getElementById('editStartDate').value = this.dataset.startDate;
                document.getElementById('editEndDate').value = this.dataset.endDate;
                
                modal.show();
            });
        });
    }

    // Save Edit functionality
    function initializeSaveEdit() {
        document.getElementById('saveEditButton').addEventListener('click', function() {
            const reminderId = document.getElementById('editReminderId').value;
            const formData = new FormData(document.getElementById('editReminderForm'));
            
            fetch(`/edit_reminder/${reminderId}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            });
        });
    }

    // Delete Reminder functionality
    function initializeDeleteReminders() {
        document.querySelectorAll('.delete-reminder').forEach(button => {
            button.addEventListener('click', function() {
                if (confirm('Bạn có chắc chắn muốn xóa nhắc nhở này?')) {
                    const reminderId = this.dataset.reminderId;
                    
                    fetch(`/delete_reminder/${reminderId}`, {
                        method: 'POST'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById(`reminder-${reminderId}`).remove();
                        } else {
                            alert(data.message);
                        }
                    });
                }
            });
        });
    }

    // Search functionality
    function initializeSearch() {
        const searchInput = document.getElementById('searchInput');
        const typeFilter = document.getElementById('typeFilter');
        const searchButton = document.getElementById('searchButton');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const reminderContainer = document.getElementById('reminderContainer');

        function createReminderCard(reminder) {
            const div = document.createElement('div');
            div.className = 'card mb-3';
            div.id = `reminder-${reminder.id}`;
            
            div.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <h5 class="card-title">${reminder.title}</h5>
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-primary edit-reminder" 
                                    data-reminder-id="${reminder.id}"
                                    data-title="${reminder.title}"
                                    data-description="${reminder.description}"
                                    data-type="${reminder.type}"
                                    data-frequency="${reminder.frequency}"
                                    data-time="${reminder.time}"
                                    data-start-date="${reminder.start_date}"
                                    data-end-date="${reminder.end_date}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-reminder" 
                                    data-reminder-id="${reminder.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <p class="card-text">${reminder.description}</p>
                    <p class="card-text">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>${reminder.time} - 
                            <i class="fas fa-calendar me-1"></i>${reminder.frequency}
                        </small>
                    </p>
                </div>
            `;
            
            return div;
        }

        function performSearch() {
            const query = searchInput.value.trim();
            const type = typeFilter.value;
            
            loadingIndicator.classList.remove('d-none');
            reminderContainer.style.opacity = '0.5';
            
            fetch(`/search_reminders?query=${encodeURIComponent(query)}&type=${encodeURIComponent(type)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        reminderContainer.innerHTML = '';
                        
                        if (data.reminders.length === 0) {
                            reminderContainer.innerHTML = `
                                <div class="alert alert-info">
                                    Không tìm thấy nhắc nhở nào phù hợp.
                                </div>
                            `;
                            return;
                        }
                        
                        data.reminders.forEach(reminder => {
                            const reminderCard = createReminderCard(reminder);
                            reminderContainer.appendChild(reminderCard);
                        });
                        
                        // Reattach event listeners
                        initializeEditReminders();
                        initializeDeleteReminders();
                    } else {
                        alert(data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Có lỗi xảy ra khi tìm kiếm');
                })
                .finally(() => {
                    loadingIndicator.classList.add('d-none');
                    reminderContainer.style.opacity = '1';
                });
        }

        // Add event listeners for search
        searchButton.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        typeFilter.addEventListener('change', performSearch);
    }

    // Initialize all functionalities
    initializeEditReminders();
    initializeSaveEdit();
    initializeDeleteReminders();
    initializeSearch();
});
