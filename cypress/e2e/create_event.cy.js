describe('Create Event page', () => {
  it('should create a single event with valid data', () => {
    // Зайдём на страницу создания события
    cy.visit('http://127.0.0.1:8000/create-event/');

    // Выбираем «Одноразовое событие»
    cy.get('#singleEvent').check();

    // После переключения типа, контейнер с формой становится видимым
    // Заполняем общие поля
    cy.get('#eventName').type('Тестовое одноразовое событие');
    cy.get('#eventComment').type('Комментарий к событию');
    cy.get('#commonTagsInput').type('тег1{enter}тег2{enter}');
    cy.get('#eventIsActive').check();

    // Заполняем поля одноразового события
    cy.get('#singleEventDate').type('2025-02-14');      // Год-месяц-день
    cy.get('#singleStartTime').type('10:00');
    cy.get('#singleDuration').type('60');
    cy.get('#singleEventStatus').select('in_process');

    // Укажем, что событие финансовое
    cy.get('#singleIsFinancial').check();

    // Заполним финансовые детали
    cy.get('#singleAmount').type('1200');
    // Выбираем аккаунт по value (например, первая опция с value="{{ account.id }}" = "1")
    cy.get('#singleEventAccount').select('1');

    // Отправляем форму
    cy.contains('Сохранить').click();

    // Дополнительно — проверяем, что форма успешно отправилась.
    // Например, если после отправки вы перенаправляете на страницу /events/:
    // cy.url().should('include', '/events/');

    // Или проверяем появление сообщения об успехе:
    cy.contains('Новое событие создано УСПЕШНО').should('be.visible');
  });
});
