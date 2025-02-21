document.addEventListener("DOMContentLoaded", function () {
    let daysCount = 7;
    const todayDate = "09.02.2025";
    const [day, month, year] = todayDate.split(".").map(num => parseInt(num, 10));
    const today = new Date(year, month - 1, day); // JS использует 0-индексацию месяцев!
    let events1 = {
        2:  ["Уборщица", "Психолог"],
        7:  ["Сдача отчёта", "Дедлайн по проекту", "Кушать шоколад"],
        9:  ["Важный звонок"]
    };

    const events = {
    "16.01.2025": ["Задача"],
    "18.01.2025": ["Дедлайн", "Проект", "Проект", "Презентация"],
    "19.01.2025": ["Встреча"],
    "22.01.2025": ["Звонок", "Проверка", "Отчёт"],
    "24.01.2025": ["Отчёт", "Проверка", "Проверка"],
    "25.01.2025": ["Проверка"],
    "29.01.2025": ["Задача", "Проверка", "Проверка", "Проект"],
    "01.02.2025": ["Звонок", "Звонок", "Звонок"],
    "04.02.2025": ["Собрание"],
    "06.02.2025": ["Звонок", "Задача", "Встреча"],
    "08.02.2025": ["Собрание", "Совещание", "Проверка", "Звонок"],
    "09.02.2025": ["Дедлайн", "Встреча"],
    "11.02.2025": ["Проект"],
    "12.02.2025": ["Дедлайн"],
    "14.02.2025": ["Дедлайн"],
    "17.02.2025": ["Дедлайн", "Совещание", "Задача"],
    "18.02.2025": ["Собрание"],
    "19.02.2025": ["Звонок", "Собрание"],
    "21.02.2025": ["Презентация"],
    "24.02.2025": ["Отчёт"],
    "27.02.2025": ["Звонок", "Проверка", "Собрание", "Проект"],
    "28.02.2025": ["Отчёт"],
    "02.03.2025": ["Звонок"],
    "06.03.2025": ["Совещание", "Звонок"],
    "10.03.2025": ["Презентация", "Задача", "Собрание"],
    "12.03.2025": ["Звонок"],
    "13.03.2025": ["Задача", "Собрание", "Встреча"],
    "14.03.2025": ["Отчёт", "Отчёт", "Задача"]
};


    const daysSelect = document.getElementById("daysCount");
    const centerTodayCheckbox = document.getElementById("centerToday");


    function generateTimeline(daysCount, centerToday = true) {

        const timelineContainer = document.querySelector('.timeline-container');
        timelineContainer.innerHTML = '<div class="timeline-line"></div>'; // Очищаем старый таймлайн

        const dayMult = 2;  // Вес дня в тикетах
        const eventMult = 1;  // Вес одного события в тикетах

        if (daysCount % 2 === 0) {
            console.warn("⚠ Четное количество дней пока не поддерживается!");
            return;
        }

        console.log("⏳ Начинаем вычислять startDate...");
        const [day, month, year] = todayDate.split(".").map(num => parseInt(num, 10));
        const startDate = new Date(year, month - 1, day); 
        startDate.setDate(startDate.getDate() - Math.floor((daysCount - 1) / 2));
        console.log("✅ startDate:", startDate);

        let totalTickets = 0; // Общая сумма тикетов
        let ticketsArray = []; // Храним тикеты для каждого дня

        let currentDate = new Date(startDate); // Создаём копию startDate


        for (let i = 0; i < daysCount; i++) {
            let dateStr = formatDate(currentDate); // Конвертируем дату в формат "DD.MM.YYYY"

            let dayTickets = dayMult;
            totalTickets += dayMult;

            if (events[dateStr]) {
                dayTickets += events[dateStr].length * eventMult;
                totalTickets += events[dateStr].length * eventMult;
            }

            ticketsArray.push({ date: dateStr, tickets: dayTickets });

            currentDate.setDate(currentDate.getDate() + 1); // Переход на следующий день
        }

        console.log("🎟️ Всего запрошено тикетов:", totalTickets);
        console.log("🎟️ Список тикетов по дням:", ticketsArray);

        // Исправляем деление на 0
        let oneTicketPrice = totalTickets > 0 ? 100 / totalTickets : 0;
        console.log("цена билета: ", oneTicketPrice);
        ticketsArray = ticketsArray.map(day => ({
            ...day,
            weight: oneTicketPrice * day.tickets
        }));

        console.log("🎟️ Итоговый список:", ticketsArray);

        let centerIndex = Math.floor(daysCount / 2);

        let leftTickets = 0;
        let rightTickets = 0;
        let leftWeight = 0;
        let rightWeight = 0;

        for (let i = 0; i < daysCount; i++) {
            let { tickets, weight } = ticketsArray[i];

            if (i < centerIndex) {
                leftTickets += tickets;
                leftWeight += weight;
            } else if (i > centerIndex) {
                rightTickets += tickets;
                rightWeight += weight;
            }
        }

        // 📌 Берём половину веса и билетов центрального дня
        let centerTickets = ticketsArray[centerIndex].tickets / 2;
        let centerWeight = ticketsArray[centerIndex].weight / 2;

        leftTickets += centerTickets;
        rightTickets += centerTickets;

        leftWeight += centerWeight;
        rightWeight += centerWeight;

        console.log("🎟️ Итоговые веса:");
        console.log("⬅ Левая часть: билеты =", leftTickets, ", вес =", leftWeight.toFixed(2));
        console.log("➡ Правая часть: билеты =", rightTickets, ", вес =", rightWeight.toFixed(2));

        // 📌 Определяем коэффициент нормализации
        let normalizationFactor = 50 / Math.max(leftWeight, rightWeight);

        // 📌 Нормализуем веса
        let normalizedLeftWeight = leftWeight * normalizationFactor;
        let normalizedRightWeight = rightWeight * normalizationFactor;

        console.log("🎯 Итоговые нормализованные веса:");
        console.log("⬅ Левая часть: нормализованный вес =", normalizedLeftWeight.toFixed(2), "%");
        console.log("➡ Правая часть: нормализованный вес =", normalizedRightWeight.toFixed(2), "%");

        // Проверяем, что сумма НЕ 100%, но сохраняет пропорции
        console.log("🔄 Проверка суммы:", (normalizedLeftWeight + normalizedRightWeight).toFixed(2), "%");

        // 📌 3. Применяем коэффициент к каждому дню
        ticketsArray = ticketsArray.map(day => ({
            ...day,
            normalizedWeight: day.weight * normalizationFactor
        }));

        // 📌 Выводим результат
        console.log("🎯 Нормализованный массив:", ticketsArray);

        let todayIndex = ticketsArray.findIndex(day => day.date === todayDate);
        console.log("🎯 todayIndex:", todayIndex);

        drawDayCenters(timelineContainer,ticketsArray, todayIndex);
        todayIndex = ticketsArray.findIndex(day => day.date === todayDate);
        drawDayTicks(timelineContainer,ticketsArray, todayIndex);

    }

    function formatDate(date) {
        return date.toLocaleDateString("ru-RU", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        });
    }


function drawDayTicks(timelineContainer, ticketsArray, todayIndex) {
    // Удалим предыдущие тики, если нужно:
    // timelineContainer.querySelectorAll(".day-tick").forEach(el => el.remove());

    // Массив, где для каждого дня будет [левая_граница, правая_граница].
    const dayBoundaries = new Array(ticketsArray.length).fill(null).map(() => [0, 0]);

    // 1) Расставляем границы для "сегодня":
    //    День todayIndex займёт ширину = ticketsArray[todayIndex].normalizedWeight
    //    Левая граница = 50% - половина его ширины
    const halfWidthToday = ticketsArray[todayIndex].normalizedWeight / 2;
    const leftToday = 50 - halfWidthToday;
    const rightToday = leftToday + ticketsArray[todayIndex].normalizedWeight;
    dayBoundaries[todayIndex] = [leftToday, rightToday];

    // 2) Идём вправо от «сегодня» (i = todayIndex+1 ... до конца)
    for (let i = todayIndex + 1; i < ticketsArray.length; i++) {
        const prevRight = dayBoundaries[i - 1][1];
        const width = ticketsArray[i].normalizedWeight;

        const left = prevRight;       // начинаем ровно там, где закончился предыдущий день
        const right = left + width;
        dayBoundaries[i] = [left, right];
    }

    // 3) Идём влево от «сегодня» (i = todayIndex-1 ... до 0)
    for (let i = todayIndex - 1; i >= 0; i--) {
        const nextLeft = dayBoundaries[i + 1][0];
        const width = ticketsArray[i].normalizedWeight;

        const right = nextLeft;       // заканчивается там, где у следующего дня начинается
        const left = right - width;
        dayBoundaries[i] = [left, right];
    }

    // 4) Собираем в общий список все граничные точки
    //    (левая + правая для каждого дня)
    let allBoundaries = [];
    dayBoundaries.forEach(bounds => {
        allBoundaries.push(bounds[0], bounds[1]);
    });

    // Сортируем (на случай, если где-то получилось < 0 или > 100)
    allBoundaries.sort((a, b) => a - b);

    // 5) Рисуем «тики» (day-tick) в контейнере
    allBoundaries.forEach(pos => {
        const tick = document.createElement("div");
        tick.className = "day-tick";
        tick.style.left = pos + "%";
        // Чтобы линия визуально шла по точке, а не слева от неё
        tick.style.transform = "translateX(-50%)";
        timelineContainer.appendChild(tick);
    });

    console.log("✅ Day boundaries:", dayBoundaries);
    console.log("✅ All sorted boundaries:", allBoundaries);
}




function drawDayCenters(timelineContainer, ticketsArray, todayIndex) {
    // Сначала очищаем старые метки (если нужно)
    // timelineContainer.querySelectorAll('.fake-center-line').forEach(el => el.remove());

    // Массив координат центров каждого дня (в процентах)
    let dayCenters = new Array(ticketsArray.length).fill(0);

    // 1) Центральный день: ставим в 50%
    dayCenters[todayIndex] = 50;

    // 2) Двигаемся влево (от todayIndex - 1 к 0)
    for (let i = todayIndex - 1; i >= 0; i--) {
        // Расстояние между центрами i и i+1 — это половина ширины i + половина ширины i+1
        let halfSum = 0.5 * (ticketsArray[i].normalizedWeight + ticketsArray[i + 1].normalizedWeight);
        // Сдвигаемся влево на halfSum от центра (i+1)-го дня
        dayCenters[i] = dayCenters[i + 1] - halfSum;
    }

    // 3) Двигаемся вправо (от todayIndex + 1 к последнему)
    for (let i = todayIndex + 1; i < ticketsArray.length; i++) {
        let halfSum = 0.5 * (ticketsArray[i].normalizedWeight + ticketsArray[i - 1].normalizedWeight);
        dayCenters[i] = dayCenters[i - 1] + halfSum;
    }

    // 4) Для каждого дня ставим «линейку» (fake-center-line)
    dayCenters.forEach((pos, i) => {
        const marker = document.createElement("div");
        marker.className = "fake-center-line";
        // `pos` уже в процентах (предполагаем, что normalizedWeight суммарно не превысит 100%)
        marker.style.left = pos + "%";
        // Смещаем саму линию, чтобы она была «по центру»
        marker.style.transform = "translateX(-50%)";
        timelineContainer.appendChild(marker);
    });

    console.log("✅ Центры дней расставлены по нормализованным весам:", dayCenters);
}


    function handleMouseMove(event) {
        let mouseX = event.clientX;
        let radius = 70;

        document.querySelectorAll(".event-marker").forEach(marker => {
            let rect = marker.getBoundingClientRect();
            let markerX = rect.left + rect.width / 2;
            let distance = Math.abs(mouseX - markerX);

            let label = marker.nextElementSibling;
            label.style.opacity = distance < radius ? "1" : "0";
        });
    }

    document.addEventListener("mousemove", handleMouseMove);
    daysSelect.addEventListener("change", () => generateTimeline(parseInt(daysSelect.value), centerTodayCheckbox.checked));
    centerTodayCheckbox.addEventListener("change", () => generateTimeline(parseInt(daysSelect.value), centerTodayCheckbox.checked));

    generateTimeline(daysCount);
});

document.addEventListener("DOMContentLoaded", function () {
    const workZoneSelect = document.getElementById("workZone");

function updateWorkZone() {
    let workZoneValue = parseInt(workZoneSelect.value);
    let remainingSpace = (100 - workZoneValue) / 2; // Левый и правый отступ

    document.querySelector(".timeline-container").style.width = workZoneValue + "vw";

    let fadeLeft = document.querySelector(".timeline-fade-left");
    let fadeRight = document.querySelector(".timeline-fade-right");
    let timelineContainer = document.querySelector(".timeline-container");

    fadeLeft.style.width = remainingSpace + "vw";
    fadeRight.style.width = remainingSpace + "vw";

    // 🛠 Фиксим смещение:
    fadeLeft.style.height = "2px";
    fadeRight.style.height = "2px";

    // 📌 Исправляем `top` с точным округлением
    let timelineTop = timelineContainer.getBoundingClientRect().top + window.scrollY;
    let newTop = Math.round(timelineTop + timelineContainer.offsetHeight / 2) - 1;

    fadeLeft.style.top = `${newTop}px`;
    fadeRight.style.top = `${newTop}px`;
}
    workZoneSelect.addEventListener("change", updateWorkZone);
    updateWorkZone(); // Устанавливаем стартовое значение

function parseSchedule(text) {
    const schedule = {};
    const lines = text.split("\n"); // Разбиваем по строкам

    for (let line of lines) {
        if (!line.trim()) continue; // Пропускаем пустые строки

        const [id, rest] = line.split(":").map(s => s.trim());
        const [date, task] = rest.split(",").map(s => s.trim());

        if (!schedule[date]) {
            schedule[date] = []; // Создаем массив, если дня еще нет
        }
        schedule[date].push(task); // Добавляем дело в нужный день
    }
    return schedule;
}    
});


