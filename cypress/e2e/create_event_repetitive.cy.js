describe('Create Event page', () => {
  it('should create a repetitive event with valid data', () => {
    // 1. Заходим на страницу
    cy.visit('http://127.0.0.1:8000/create-event/');

    // 2. Выбираем «Повторяющееся событие»
    cy.get('#repetitiveEvent').check();

    // 3. Заполняем общие поля
    cy.get('#eventName').type('Тестовое повторяющееся событие');
    cy.get('#eventComment').type('Комментарий для многократного события');
    cy.get('#commonTagsInput').type('тегА{enter}тегБ{enter}');
    cy.get('#eventIsActive').check();

    // 4. Настройки повторения (пример: повторять по дням недели)
    // Предположим, у нас три Radio-кнопки:
    //    * days_of_week
    //    * very_date
    //    * n_days
    // и поле для ввода "Пн, Ср, Пт"
    cy.get('[name="repetitiveTypeRadio"]').check('days_of_week');
    cy.get('[name="days_of_week"][value="monday"]').check();
    cy.get('[name="days_of_week"][value="wednesday"]').check();
    cy.get('[name="days_of_week"][value="friday"]').check();

    // Задаём период, в пределах которого это будет повторяться
    cy.get('#repetitiveStartDate').type('2025-02-01');
    cy.get('#repetitiveEndDate').type('2025-03-01');

    // Укажем время начала и продолжительность
    cy.get('#repetitiveStartTime').type('09:30');
    cy.get('#repetitiveDuration').type('90');

    // Ставим статус, например «in_process»
    cy.get('#repetitiveEventStatus').select('in_process');

    // Укажем, что событие финансовое
    cy.get('#repetitiveIsFinancial').check();
    cy.get('#repetitiveAmount').type('500');

    // Выбираем аккаунт (как и в случае с одноразовым)
    cy.get('#repetitiveEventAccount').select('1');

    // 5. Отправляем форму
    cy.contains('Сохранить').click();

    // 6. Проверяем результат
    // Тут могут быть разные варианты:
    cy.contains('Новое событие создано УСПЕШНО').should('be.visible');
  });
});
