$(document).ready(function() {
    // Функция для отображения модального окна с сообщением
    function showModal(message) {
        $('#success-message').text(message);
        $('#success-modal').css('display', 'block');
    }

    // Функция для закрытия модального окна
    function closeModal() {
        $('#success-modal').css('display', 'none');
    }

    // Обработка успешного ответа после отправки задачи
    function handleSuccess() {
        var teacherSelect = $('#teacher-select');
        var taskContent = $('#task-content');

        var selectedTeacher = teacherSelect.find('option:selected').text();
        var taskMessage = 'Вы успешно отправили задачу учителю ' + selectedTeacher;

        if (teacherSelect.val() && taskContent.val()) {
            showModal(taskMessage);
        }

        // Очистка значений полей формы
        teacherSelect.val('');
        taskContent.val('');
    }

    // Закрытие модального окна при клике на кнопку "OK"
    $('#ok-button').click(function() {
        closeModal();
    });

    // Отправка формы
    $('#task-form').submit(function(event) {
        event.preventDefault(); // Отмена стандартной отправки формы

        handleSuccess();
    });
});
