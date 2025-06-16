export const weekdays = {
    full_EN:  ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    short_EN: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    full_RU:  ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
    short_RU: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
}

function getMonthInfo(year: number, month: number) {
    const firstDay = new Date(year, month - 1, 1)        // JS считает месяцы с нуля
    const lastDay = new Date(year, month, 0)             // 0-й день следующего месяца = последний день текущего

    const totalDays = lastDay.getDate()                  // сколько всего дней
    const weekDayOfFirst = firstDay.getDay()             // 0 — воскресенье, 1 — понедельник, и т.д.

    return {
        totalDays,
        weekDayOfFirst
    }
}

// Возвращает номер дня недели (1 = Понедельник, 7 = Воскресенье)
export function getDayNumber(input: string | number): number {
    const dayMap: Record<string, number> = {
        // Понедельник
        '1': 1, 'monday': 1, 'mon': 1, 'понедельник': 1, 'пн': 1,
        // Вторник
        '2': 2, 'tuesday': 2, 'tue': 2, 'вторник': 2, 'вт': 2,
        // Среда
        '3': 3, 'wednesday': 3, 'wed': 3, 'среда': 3, 'ср': 3,
        // Четверг
        '4': 4, 'thursday': 4, 'thu': 4, 'четверг': 4, 'чт': 4,
        // Пятница
        '5': 5, 'friday': 5, 'fri': 5, 'пятница': 5, 'пт': 5,
        // Суббота
        '6': 6, 'saturday': 6, 'sat': 6, 'суббота': 6, 'сб': 6,
        // Воскресенье
        '7': 7, 'sunday': 7, 'sun': 7, 'воскресенье': 7, 'вс': 7,
    }

    if (typeof input === 'number' && input >= 1 && input <= 7) {
        return input
    }

    const key = String(input).trim().toLowerCase()
    const number = dayMap[key]

    if (!number) {
        throw new Error(`Неверный ввод: "${input}"`)
    }

    return number
}

// Возвращает название дня недели по номеру
export function getDayName(day: number, format: 'full_EN' | 'short_EN' | 'full_RU' | 'short_RU' = 'full_EN'): string {
    const formats = {
        full_EN:  ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        short_EN: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        full_RU:  ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
        short_RU: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
    }

    if (!(day >= 1 && day <= 7)) {
        throw new Error(`Номер дня должен быть от 1 до 7: ${day}`)
    }

    return formats[format][day - 1]
}

/**
 * Возвращает массив всех дней месяца с сокращённым названием дня недели на русском.
 * @param year Год, например: 2025
 * @param month Месяц (1 — Январь, 12 — Декабрь)
 */
export function getMonthDaysWithWeekdays(year: number, month: number): { day: number, weekday: string }[] {
    const result = []
    const daysInMonth = new Date(year, month, 0).getDate()

    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month - 1, day)
        const weekdayIndex = date.getDay() // 0 — Sunday, 6 — Saturday

        // Преобразуем: 0 (вс) → 7, 1 (пн) → 1, … 6 (сб) → 6
        const normalizedIndex = weekdayIndex === 0 ? 7 : weekdayIndex

        const weekdayRU = weekdays.short_RU[normalizedIndex - 1]
        result.push({ day, weekday: weekdayRU })
    }

    return result
}

console.log(getMonthDaysWithWeekdays(2025, 5))