document.addEventListener("DOMContentLoaded", function () {
    let daysCount = 30;
    const todayDate = 9;
    const events = {
        2:  ["Уборщица", "Психолог"],
        7:  ["Сдача отчёта", "Дедлайн по проекту", "Кушать шоколад"],
        9:  ["Важный звонок"]
    };

    const daysSelect = document.getElementById("daysCount");
    const centerTodayCheckbox = document.getElementById("centerToday");

    function generateTimeline(daysCount, centerToday = false) {
    const timelineContainer = document.querySelector('.timeline-container');
    timelineContainer.innerHTML = '<div class="timeline-line"></div>'; // Очищаем старый таймлайн

    let baseWidth = 100 / (daysCount * 2);
    const widthMult = 1.4;
    baseWidth = baseWidth * widthMult;
    let totalTasks = Object.values(events).flat().length;

    let rawWidths = [];
    for (let i = 1; i <= daysCount; i++) {
        let taskCount = events[i] ? events[i].length : 0;
        let extraWidth = totalTasks ? (taskCount / totalTasks) * (100 - daysCount * baseWidth) : 0;
        rawWidths.push(baseWidth + extraWidth);
    }

    let totalRawWidth = rawWidths.reduce((acc, w) => acc + w, 0);
    let dayWidths = rawWidths.map(w => (w / totalRawWidth) * 100);

    let html = "";
    let currentLeft = 0;
    let todayPosition = 0; // Позиция "сегодня" для центрирования
    let lastTickPosition = 0; // Запомним последнюю засечку

    for (let day = 1; day <= daysCount; day++) {
        let w = dayWidths[day - 1];
        let dayLeft = currentLeft;
        let dayRight = currentLeft + w;
        let dayCenter = (dayLeft + dayRight) / 2;

        html += `<div class="day-tick" style="left: ${dayLeft}%;"></div>`;

        if (day === todayDate) {
            html += `<div class="today-highlight" style="left: ${dayLeft}%; width: ${w}%;"></div>`;
            todayPosition = dayCenter;
        }

        let dateObj = new Date(2025, 1, day);
        let weekdayStr = dateObj.toLocaleDateString("ru-RU", { weekday: "short" });
        html += `
            <div class="day-label-group" style="left: ${dayCenter}%;"><div class="day-label">${day}</div><div class="weekday-label">${weekdayStr}</div></div>
        `;

        if (events[day]) {
            let numEvents = events[day].length;
            for (let i = 0; i < numEvents; i++) {
                let frac = (i + 1) / (numEvents + 1);
                let eventX = dayLeft + frac * (dayRight - dayLeft);
                let eventText = events[day][i];

                html += `
                    <div class="event-marker" style="left: ${eventX}%;" data-event="${eventText}"></div>
                    <div class="event-label" style="left: ${eventX}%;">${eventText}</div>
                `;
            }
        }
        
        lastTickPosition = dayRight; // Запоминаем последнюю засечку
        currentLeft = dayRight;
    }

    // Исправляем последнюю засечку, чтобы не выходила за пределы
    html += `<div class="day-tick" style="left: calc(${lastTickPosition}% - 2px);"></div>`;

    timelineContainer.innerHTML += html;

    // 🎯 Центрирование на сегодня
    if (centerToday) {
        requestAnimationFrame(() => {
            let containerWidth = timelineContainer.clientWidth;
            let scrollAmount = (todayPosition / 100) * timelineContainer.scrollWidth - containerWidth / 2;
            timelineContainer.scrollTo({ left: scrollAmount, behavior: "smooth" });
        });
    }
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
});


