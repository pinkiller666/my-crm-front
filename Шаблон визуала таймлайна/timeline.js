// timeline.js (комбинированный)
// Этот код предполагает, что в HTML есть элементы:
// <div class="timeline-container"></div>
// <select id="daysCount">...</select>, <input type="checkbox" id="centerToday" ...>
// <select id="workZone">...</select>, и т.п.
// а также подключен файл timeline.css

document.addEventListener("DOMContentLoaded", function () {
    // -------------------- Настройки --------------------
    let daysCount = 7;                          // стартовое количество дней
    const todayDateStr = "09.02.2025";          // сегодняшняя дата (дд.мм.гггг)
    // Подсказка: можно вытащить из сервера или реального today, но здесь - жёстко
    const [dayNum, monthNum, yearNum] = todayDateStr.split(".").map(num => parseInt(num, 10));
    const today = new Date(yearNum, monthNum - 1, dayNum);

    // Пример событий: ключ = "DD.MM.YYYY", значение = массив строк
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
        "09.02.2025": ["Дедлайн", "Встреча"], // сегодняшний день
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

    // Находим элементы управления
    const daysSelect = document.getElementById("daysCount");
    const centerTodayCheckbox = document.getElementById("centerToday");
    const timelineContainer = document.querySelector(".timeline-container");

    // -------------------- Основная функция --------------------
    function generateTimeline(daysCount, centerToday = true) {
        // timelineContainer.innerHTML = '<div class="timeline-line"></div>';
        // вместо этого просто очищаем контейнер:
        timelineContainer.innerHTML = '';

        // 2) Параметры «билетов»
        const dayMult = 2;   // базовый вес дня
        const eventMult = 1; // вес одного события

        if (daysCount % 2 === 0) {
            console.warn("⚠ Чётное количество дней пока не поддерживается!");
            return;
        }

        // 3) Определяем стартовую дату = сегодня - (daysCount-1)/2
        const [d, m, y] = todayDateStr.split(".").map(num => parseInt(num, 10));
        let startDate = new Date(y, m - 1, d);
        startDate.setDate(startDate.getDate() - Math.floor((daysCount - 1) / 2));

        // 4) Собираем в массив (ticketsArray) данные: { date: "DD.MM.YYYY", tickets, weight... }
        let totalTickets = 0;
        let ticketsArray = [];
        let currentDate = new Date(startDate);

        for (let i = 0; i < daysCount; i++) {
            let dateStr = formatDate(currentDate);
            let dayTickets = dayMult;
            if (events[dateStr]) {
                dayTickets += events[dateStr].length * eventMult;
            }
            ticketsArray.push({ date: dateStr, tickets: dayTickets });
            totalTickets += dayTickets;

            currentDate.setDate(currentDate.getDate() + 1);
        }

        // 5) «Цена билета» -> распределяем 100% среди всех дней
        let oneTicketPrice = totalTickets > 0 ? 100 / totalTickets : 0;
        ticketsArray.forEach(obj => {
            obj.weight = obj.tickets * oneTicketPrice; 
        });

        // 6) Центральный индекс (где «сегодня» должен быть)
        let centerIndex = Math.floor(daysCount / 2);
        // Считаем левые/правые суммы для нормализации:
        let leftTickets = 0, rightTickets = 0;
        let leftWeight = 0, rightWeight = 0;

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
        // половина билетов центрального дня уходит влево, половина - вправо
        let centerTickets = ticketsArray[centerIndex].tickets / 2;
        let centerWeight = ticketsArray[centerIndex].weight / 2;
        leftTickets += centerTickets;  leftWeight += centerWeight;
        rightTickets += centerTickets; rightWeight += centerWeight;

        // Коэффициент нормализации, чтобы левая/правая часть уложились ~ по 50%:
        let normalizationFactor = 50 / Math.max(leftWeight, rightWeight);

        // Присваиваем каждому дню «normalizedWeight»
        ticketsArray.forEach(obj => {
            obj.normalizedWeight = obj.weight * normalizationFactor;
        });

        // 7) Найдём индекс «сегодня», чтобы понять, где рисовать highlight
        let todayIndex = ticketsArray.findIndex(obj => obj.date === todayDateStr);
        if (todayIndex === -1) {
            console.warn("Сегодняшняя дата не найдена среди диапазона!");
            todayIndex = centerIndex; // fallback
        }

        console.log("ticketsArray", ticketsArray);

        const extraDays = 10;

        // 1) Определим самые «левые» и «правые» даты, которые уже есть в массиве:
        let leftmostDate = parseDate(ticketsArray[0].date);  // первый день в массиве
        let rightmostDate = parseDate(ticketsArray[ticketsArray.length - 1].date); // последний

        // 2) Функция вычисляет dayTickets/weight/normalizedWeight для заданной даты
        function buildDayObject(dateObj) {
            let dateStr = formatDate(dateObj);
            // Базовые билеты
            let dayTickets = dayMult;
            // Если есть события, добавим eventMult за каждое
            if (events[dateStr]) {
                dayTickets += events[dateStr].length * eventMult;
            }
            // Вес до нормализации
            let weight = dayTickets * oneTicketPrice;
            // Применяем *старый* normalizationFactor
            let normalizedWeight = weight * normalizationFactor;
            return {
                date: dateStr,
                tickets: dayTickets,
                weight: weight,
                normalizedWeight: normalizedWeight
            };
        }

        // 3) Добавляем дни «слева» (до leftmostDate)
        for (let i = 1; i <= extraDays; i++) {
            // например: leftmostDate - i
            let newDate = new Date(
                leftmostDate.getFullYear(),
                leftmostDate.getMonth(),
                leftmostDate.getDate() - i
            );
            ticketsArray.push(buildDayObject(newDate));
        }

        // 4) Добавляем дни «справа» (после rightmostDate)
        for (let i = 1; i <= extraDays; i++) {
            let newDate = new Date(
                rightmostDate.getFullYear(),
                rightmostDate.getMonth(),
                rightmostDate.getDate() + i
            );
            ticketsArray.push(buildDayObject(newDate));
        }

        // 5) Упорядочим массив по реальным датам, чтобы слева-направо шли по возрастанию
        ticketsArray.sort((a, b) => parseDate(a.date) - parseDate(b.date));
        console.log("Расширенный ticketsArray", ticketsArray);

        // -- теперь в ticketsArray на 20 объектов больше, чем было.
        // -- при этом у «новых» дней weight/normalizedWeight посчитаны по старому фактору.

        
        // 6) Теперь ещё раз ищем «сегодня»
        todayIndex = ticketsArray.findIndex(obj => obj.date === todayDateStr);
        console.log("Индекс сегодняшей даты: ", todayIndex);
        if (todayIndex === -1) {
            console.warn("Сегодняшняя дата не найдена среди расширенного диапазона!");
            // fallback: todayIndex = ...
        }
        

        // 8) Расчитываем границы (dayBoundaries) каждого дня в процентах
        const dayBoundaries = computeDayBoundaries(ticketsArray, todayIndex);

        // 9) Рисуем тики (вертикальные полоски по границам)
        drawTicks(timelineContainer, dayBoundaries);

        // 10) Добавим разметку для каждого дня: highlight, лейблы, события
        for (let i = 0; i < ticketsArray.length; i++) {
            let dayObj = ticketsArray[i];
            let [leftPerc, rightPerc] = dayBoundaries[i];
            let dayCenter = (leftPerc + rightPerc) / 2;

            // Подсветка сегодняшнего дня
            if (i === todayIndex) {
                let highlight = document.createElement("div");
                highlight.className = "today-highlight";
                highlight.style.left = leftPerc + "%";
                highlight.style.width = (rightPerc - leftPerc) + "%";
                timelineContainer.appendChild(highlight);
            }

            // Метка дня: число + сокращённый день недели
            addDayLabel(timelineContainer, dayObj.date, dayCenter);

            // События
            if (events[dayObj.date]) {
                let arr = events[dayObj.date];
                // Развесим события более-менее равномерно между leftPerc и rightPerc
                for (let eIndex = 0; eIndex < arr.length; eIndex++) {
                    let frac = (eIndex + 1) / (arr.length + 1);
                    let eventX = leftPerc + frac * (rightPerc - leftPerc);
                    let eventTitle = arr[eIndex];
                    addEventMarker(timelineContainer, eventX, eventTitle);
                }
            }
        }

        avoidOverlapEventLabels();

        // !!!TODO!!!
        // 11) Если включено «центрировать сегодня» — прокрутить
        if (centerToday) {
            requestAnimationFrame(() => {
                let containerWidth = timelineContainer.clientWidth;
                let todayCenter = (dayBoundaries[todayIndex][0] + dayBoundaries[todayIndex][1]) / 2;
                let scrollX = (todayCenter / 100) * timelineContainer.scrollWidth - containerWidth / 2;
                timelineContainer.scrollTo({ left: scrollX, behavior: "smooth" });
            });
        }
    }

    // -------------------- Вспомогательные функции --------------------

    // Формат "дд.мм.гггг" -> объект Date
    function parseDate(strDate) {
        let [d, m, y] = strDate.split(".").map(Number);
        return new Date(y, m - 1, d);
    }

    // "DD.MM.YYYY"
    function formatDate(dateObj) {
        return dateObj.toLocaleDateString("ru-RU", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        });
    }

    // Вычисляем [ [left, right], [left, right], ... ] для каждого дня
    function computeDayBoundaries(ticketsArray, todayIndex) {
        let arrLength = ticketsArray.length;
        let dayBoundaries = new Array(arrLength).fill(null).map(()=>[0,0]);

        // центральный день
        let halfW = ticketsArray[todayIndex].normalizedWeight / 2;
        let leftToday = 50 - halfW;
        let rightToday = leftToday + ticketsArray[todayIndex].normalizedWeight;
        dayBoundaries[todayIndex] = [leftToday, rightToday];

        // вправо (i = todayIndex+1 ... конец)
        for (let i = todayIndex + 1; i < arrLength; i++) {
            let prevRight = dayBoundaries[i - 1][1];
            let width = ticketsArray[i].normalizedWeight;
            let left = prevRight;
            let right = left + width;
            dayBoundaries[i] = [left, right];
        }

        // влево (i = todayIndex-1 ... 0)
        for (let i = todayIndex - 1; i >= 0; i--) {
            let nextLeft = dayBoundaries[i + 1][0];
            let width = ticketsArray[i].normalizedWeight;
            let right = nextLeft;
            let left = right - width;
            dayBoundaries[i] = [left, right];
        }

        return dayBoundaries;
    }

    // Рисуем «тики» (day-tick) по всем граничным точкам
    function drawTicks(container, dayBoundaries) {
        let allPoints = [];
        dayBoundaries.forEach(([l, r])=>{
            allPoints.push(l, r);
        });
        allPoints.sort((a,b)=>a-b);

        allPoints.forEach(pos => {
            let tick = document.createElement("div");
            tick.className = "day-tick";
            let newPos = pos
            if(pos == 0){
                newPos = 1
            }else if(pos == 100){
                newPos = 99
            }
            tick.style.left = newPos + "%";
            tick.style.transform = "translateX(-50%)";
            container.appendChild(tick);
        });
    }

    // Добавляем в контейнер блок с меткой дня (число + «пн», «вт» и т.п.)
    function addDayLabel(container, dateStr, centerPerc) {
        let dateObj = parseDate(dateStr);
        let dayNumber = dateObj.getDate();
        let weekdayStr = dateObj.toLocaleDateString("ru-RU", { weekday: "short" });

        let group = document.createElement("div");
        group.className = "day-label-group";
        group.style.left = centerPerc + "%";
        group.style.transform = "translateX(-50%)";

        let dayLabel = document.createElement("div");
        dayLabel.className = "day-label";
        dayLabel.textContent = dayNumber;

        let wday = document.createElement("div");
        wday.className = "weekday-label";
        wday.textContent = weekdayStr;

        group.appendChild(dayLabel);
        group.appendChild(wday);
        container.appendChild(group);
    }

    // Добавляем event-marker и event-label
    function addEventMarker(container, leftPerc, text) {
        let marker = document.createElement("div");
        marker.className = "event-marker";
        marker.style.left = leftPerc + "%";
        container.appendChild(marker);

        let label = document.createElement("div");
        label.className = "event-label";
        label.style.left = leftPerc + "%";
        label.textContent = text;
        container.appendChild(label);
    }

    // -------------------- Наведение мышкой (подсветка event) --------------------
function handleMouseMove(event) {
    let mouseX = event.clientX;
    let mouseY = event.clientY;
    let radius = Math.max(140, window.innerWidth * 0.05);

    document.querySelectorAll(".event-marker").forEach(marker => {
        let rect = marker.getBoundingClientRect();
        let markerX = rect.left + rect.width / 2; // Центр по X
        let markerY = rect.top + rect.height / 2; // Центр по Y

        // Вычисляем реальное расстояние от курсора до центра точки
        let distance = Math.sqrt((mouseX - markerX) ** 2 + (mouseY - markerY) ** 2);

        let label = marker.nextElementSibling;
        if (!label) return;

        // Показываем подпись только если курсор попадает в круг радиуса `radius`
        label.style.opacity = (distance < radius) ? "1" : "0";
    });
}
        document.addEventListener("mousemove", handleMouseMove);

        // -------------------- Слушатели на селекторы --------------------
        daysSelect.addEventListener("change", () => {
            generateTimeline(parseInt(daysSelect.value), centerTodayCheckbox.checked);
        });
        centerTodayCheckbox.addEventListener("change", () => {
            generateTimeline(parseInt(daysSelect.value), centerTodayCheckbox.checked);
        });

        // -------------------- Стартовый вызов --------------------
        generateTimeline(daysCount);
    });


function avoidOverlapEventLabels() {
  // Собираем массив лейблов
  const labels = Array.from(document.querySelectorAll(".event-label"));
  
  // Сортируем лейблы по горизонтальной координате (left)
  labels.sort((a, b) => {
    // Получим left центра или левого края
    const aRect = a.getBoundingClientRect();
    const bRect = b.getBoundingClientRect();
    return aRect.left - bRect.left;
  });

  // Функция, проверяющая пересечение двух DOM-элементов
  function isOverlap(rect1, rect2) {
    return !(
      rect1.right < rect2.left ||
      rect1.left > rect2.right ||
      rect1.bottom < rect2.top ||
      rect1.top > rect2.bottom
    );
  }

  // Проходим по всем лейблам
  for (let i = 0; i < labels.length; i++) {
    const current = labels[i];
    // Начальное «смещение вверх» (относительно изначального top)
    let shift = 0;



    // Получим изначальную позицию current
    const currentRect = current.getBoundingClientRect();

    // Для удобства запомним изначальный offsetTop
    // (или храним где-то начальное style.top)
    const baseTop = parseFloat(current.style.top) || 0;

    // Сравниваем со всеми предыдущими лейблами, которые уже расставлены
    for (let j = 0; j < i; j++) {
      const other = labels[j];
      const otherRect = other.getBoundingClientRect();

      // Проверяем, пересекаются ли current и other 
      // при текущем shift
      let newRect = {
        left: currentRect.left,
        right: currentRect.right,
        top: currentRect.top - shift, // двигаем вверх
        bottom: currentRect.bottom - shift
      };

      // Пока пересекаются  увеличиваем shift
      if (isOverlap(newRect, otherRect)) {
        shift += 1; // двигаем ещё на 20px выше
        // пересчитываем координаты newRect
        newRect.top = currentRect.top - shift;
        newRect.bottom = currentRect.bottom - shift;
        requestAnimationFrame(() => {
            current.style.top = (baseTop - shift) + "px";
        });
      }
    }

    setTimeout(() => {
        const currentRect = current.getBoundingClientRect();
    }, 0);
    // Устанавливаем style.top с учётом итогового shift
    // (сдвигаем вверх от исходной позиции)
    if (shift > 0) {
      current.style.top = (baseTop - shift) + "px";
    }
    setTimeout(() => {
        const currentRect = current.getBoundingClientRect();
    }, 0);
  }
}


// ---- Отдельно: работа с #workZone, fade-линиями и т.д. ----
document.addEventListener("DOMContentLoaded", function () {
    const workZoneSelect = document.getElementById("workZone");

    function updateWorkZone() {
        let workZoneValue = parseInt(workZoneSelect.value);
        let remainingSpace = (100 - workZoneValue) / 2; // Левый и правый отступ

        const timelineContainer = document.querySelector(".timeline-container");
        timelineContainer.style.width = workZoneValue + "vw";

        let fadeLeft = document.querySelector(".timeline-fade-left");
        let fadeRight = document.querySelector(".timeline-fade-right");

        fadeLeft.style.width = remainingSpace + "vw";
        fadeRight.style.width = remainingSpace + "vw";

        fadeLeft.style.height = "2px";
        fadeRight.style.height = "2px";

        let timelineTop = timelineContainer.getBoundingClientRect().top + window.scrollY;
        let newTop = Math.round(timelineTop + timelineContainer.offsetHeight / 2) - 1;

        // fadeLeft.style.top = `${newTop}px`;
        // fadeRight.style.top = `${newTop}px`;
        // Обновляем ширину линии, чтобы она совпадала с контейнером
        document.documentElement.style.setProperty('--timeline-width', `${workZoneValue}vw`);

    }
    workZoneSelect.addEventListener("change", updateWorkZone);

    updateWorkZone();
});


document.addEventListener("DOMContentLoaded", function () {
    const timelineContainer = document.querySelector(".timeline-container");

    // === 1. Горизонтальный скролл при прокрутке колеса (Shift + колесо)
    timelineContainer.addEventListener("wheel", function (e) {
        if (e.deltaY !== 0) {  // Игнорируем если пользователь просто скроллит вверх/вниз
            e.preventDefault();
            timelineContainer.scrollLeft += e.deltaY * 2; // Ускоряем движение
        }
    });

    // === 2. Drag & Drop скроллинг (как в Trello)
    let isDragging = false;
    let startX, scrollLeft;

    timelineContainer.addEventListener("mousedown", (e) => {
        isDragging = true;
        startX = e.pageX - timelineContainer.offsetLeft;
        scrollLeft = timelineContainer.scrollLeft;
        timelineContainer.classList.add("dragging"); // Добавляем эффект курсора
    });

    timelineContainer.addEventListener("mouseleave", () => isDragging = false);
    timelineContainer.addEventListener("mouseup", () => {
        isDragging = false;
        timelineContainer.classList.remove("dragging"); // Убираем эффект курсора
    });

    timelineContainer.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        e.preventDefault();
        const x = e.pageX - timelineContainer.offsetLeft;
        const walk = (x - startX) * 1.5; // Чем больше множитель, тем быстрее
        timelineContainer.scrollLeft = scrollLeft - walk;
    });

/*    // === 3. Добавляем кнопки "←" и "→" для удобства
    const leftButton = document.createElement("button");
    leftButton.className = "timeline-scroll-btn left";
    leftButton.innerHTML = "←";
    leftButton.addEventListener("click", () => timelineContainer.scrollBy({ left: -200, behavior: "smooth" }));

    const rightButton = document.createElement("button");
    rightButton.className = "timeline-scroll-btn right";
    rightButton.innerHTML = "→";
    rightButton.addEventListener("click", () => timelineContainer.scrollBy({ left: 200, behavior: "smooth" }));

    document.body.appendChild(leftButton);
    document.body.appendChild(rightButton);*/

    function updateDayLabelsVisibility() {
      // Берём координаты видимой области контейнера
      const containerRect = timelineContainer.getBoundingClientRect();

      // Проходимся по всем элементам дня
      document.querySelectorAll(".day-label-group").forEach(labelGroup => {
        const groupRect = labelGroup.getBoundingClientRect();
        
        // Проверяем, целиком ли находится элемент в зоне контейнера
        if (
          groupRect.left >= containerRect.left &&
          groupRect.right <= containerRect.right
        ) {
          labelGroup.style.opacity = 1;
        } else {
          labelGroup.style.opacity = 0;
        }
      });
    }

    // Вызываем при прокрутке, изменении размеров и после генерации таймлайна
    timelineContainer.addEventListener("scroll", updateDayLabelsVisibility);
    window.addEventListener("resize", updateDayLabelsVisibility);
    updateDayLabelsVisibility();
});
