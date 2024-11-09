document.addEventListener('DOMContentLoaded', function() {
    // Xử lý tìm kiếm và lọc
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    const searchButton = document.getElementById('searchButton');
    const reminderCards = document.querySelectorAll('.reminder-card');

    function filterReminders() {
        const searchTerm = searchInput.value.toLowerCase();
        const filterType = typeFilter.value;

        reminderCards.forEach(card => {
            const title = card.querySelector('.card-title').textContent.toLowerCase();
            const description = card.querySelector('.card-text').textContent.toLowerCase();
            const type = card.getAttribute('data-type');

            const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
            const matchesType = filterType === '' || type === filterType;

            card.style.display = matchesSearch && matchesType ? 'block' : 'none';
        });
    }

    searchButton.addEventListener('click', filterReminders);
    searchInput.addEventListener('keyup', filterReminders);
    typeFilter.addEventListener('change', filterReminders);

    // Xử lý chỉnh sửa nhắc nhở
    const editButtons = document.querySelectorAll('.edit-reminder');
    const editModal = new bootstrap.Modal(document.getElementById('editReminderModal'));
    const saveEditButton = document.getElementById('saveEditButton');

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reminderId = this.getAttribute('data-reminder-id');
            const title = this.getAttribute('data-title');
            const description = this.getAttribute('data-description');
            const type = this.getAttribute('data-type');
            const frequency = this.getAttribute('data-frequency');
            const time = this.getAttribute('data-time');
            const startDate = this.getAttribute('data-start-date');
            const endDate = this.getAttribute('data-end-date');

            // Điền thông tin vào form chỉnh sửa
            document.getElementById('editReminderId').value = reminderId;
            document.getElementById('editTitle').value = title;
            document.getElementById('editDescription').value = description;
            document.getElementById('editType').value = type;
            document.getElementById('editFrequency').value = frequency;
            document.getElementById('editTime').value = time;
            document.getElementById('editStartDate').value = startDate;
            document.getElementById('editEndDate').value = endDate;

            editModal.show();
        });
    });

    // Xử lý lưu chỉnh sửa
    saveEditButton.addEventListener('click', function() {
        const formData = new FormData(document.getElementById('editReminderForm'));
        const reminderId = document.getElementById('editReminderId').value;

        fetch(`/edit_reminder/${reminderId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Tải lại trang để hiển thị cập nhật
            } else {
                alert('Có lỗi xảy ra khi cập nhật nhắc nhở');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi cập nhật nhắc nhở');
        });
    });

    // Xử lý xóa nhắc nhở
    const deleteButtons = document.querySelectorAll('.delete-reminder');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Bạn có chắc chắn muốn xóa nhắc nhở này?')) {
                const reminderId = this.getAttribute('data-reminder-id');

                fetch(`/delete_reminder/${reminderId}`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload(); // Tải lại trang để cập nhật danh sách
                    } else {
                        alert('Có lỗi xảy ra khi xóa nhắc nhở');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Có lỗi xảy ra khi xóa nhắc nhở');
                });
            }
        });
    });
}); 