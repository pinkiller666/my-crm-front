import plotly.graph_objects as go
from datetime import datetime, timedelta
from .models import MoneyEvent


class TimelineDrawer:
    def __init__(self, events):

        self.events = events
        self.dates = [event.single_event_date for event in self.events]

        self.names = [event.name for event in self.events]

        # Точка "сегодня" (без часов/минут)
        self.today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Примерная логика для start_date и end_date:
        # - берём "сегодня" и смещаемся назад на ~7 дней и вперёд на ~40.
        # - плюс в примере вы делали replace(day=1) и т.п. — оставим это как есть:
        self.start_date = (self.today.replace(day=1) - timedelta(days=7)).replace(day=25)
        self.end_date = (self.today.replace(day=1) + timedelta(days=40)).replace(day=15)

        # Генерируем «линейку» дат с шагом в 1 день
        self.tick_dates = [
            self.start_date + timedelta(days=i)
            for i in range((self.end_date - self.start_date).days + 1)
        ]

        # Сгруппируем события по датам
        self.events_by_date = self.group_events_by_date()

    def group_events_by_date(self):
        grouped = {}
        for event, date in zip(self.names, self.dates):
            if date in grouped:
                grouped[date].append(event)
            else:
                grouped[date] = [event]
        return grouped

    def draw_timeline(self):
        fig = go.Figure()

        # Фоновые «подсветки» месяцев
        self.add_month_backgrounds(fig)

        # Линия времени (розовая горизонтальная)
        fig.add_trace(go.Scatter(
            x=[self.tick_dates[0], self.tick_dates[-1]],
            y=[0, 0],
            mode="lines",
            line=dict(color="pink", width=2),
            name="Линия времени"
        ))

        # Вертикальные деления для каждого дня (с надписью дня месяца)
        self.add_day_ticks(fig)

        # Сами события (красные точки + подписи)
        self.add_events(fig)

        # «Сейчас» — вертикальная линия (с надписью «Сегодняшний день»)
        self.add_today_marker(fig)

        # Настройки оформления осей и высоты
        fig.update_layout(
            title="Временная линия",
            xaxis_title="",
            yaxis=dict(visible=False),
            xaxis=dict(
                showgrid=True,
                zeroline=False,
                showline=True,
                showticklabels=False,
                range=[self.start_date, self.end_date],
            ),
            plot_bgcolor="white",
            height=400
        )

        return fig

    def add_month_backgrounds(self, fig):
        # Заливка под каждый день, в примере логика: текущий месяц (розоватый),
        # прошлый и следующий — зеленоватые
        for date in self.tick_dates:
            if date.month == self.today.month:
                color = "rgba(255, 192, 203, 0.2)"  # Розовый для текущего месяца
            elif date < self.today.replace(day=1):
                color = "rgba(144, 238, 144, 0.2)"  # Зелёный для предыдущего месяца
            else:
                color = "rgba(144, 238, 144, 0.2)"  # Зелёный для следующего месяца

            fig.add_shape(
                type="rect",
                x0=date,
                x1=date + timedelta(days=1),
                y0=-1,
                y1=1,
                fillcolor=color,
                line=dict(width=0),
                layer="below"
            )

    def add_day_ticks(self, fig):
        for date in self.tick_dates:
            line_length = 0.2
            color = "gray"
            text_size = 12

            # Скажем, если это 1-е число месяца — шрифт побольше:
            if date.day == 1:
                text_size = 32

            fig.add_trace(go.Scatter(
                x=[date, date],
                y=[-line_length, line_length],
                mode="lines+text",
                line=dict(color=color, width=1),
                text=[str(date.day)],
                textposition="bottom center",
                textfont=dict(family="Comfortaa", size=text_size, color="gray", weight="bold"),
                showlegend=False
            ))

    def add_events(self, fig):
        # Раскладываем события в пределах одного дня «по Y», чтобы не наслаивались
        for date, events in self.events_by_date.items():
            num_events = len(events)
            if num_events > 1:
                offsets = [i * 0.3 / (num_events - 1) - 0.15 for i in range(num_events)]
            else:
                offsets = [0]

            for event, offset in zip(events, offsets):
                fig.add_trace(go.Scatter(
                    x=[date + timedelta(hours=12)],  # Сдвиг в полдень
                    y=[offset],
                    mode="markers+text",
                    marker=dict(size=10, color="red"),
                    text=[event],
                    textposition="top center",
                    textfont=dict(family="Comfortaa", size=12, color="black"),
                    showlegend=False
                ))

    def add_today_marker(self, fig):
        fig.add_shape(
            type="line",
            x0=self.today,
            x1=self.today,
            y0=-0.5,
            y1=1,
            line=dict(color="#FF69B4", width=4, dash="solid"),
            layer="above"
        )
        fig.add_trace(go.Scatter(
            x=[self.today],
            y=[-0.7],
            mode="text",
            text=["Сегодняшний день"],
            textfont=dict(family="Comfortaa", size=20, color="pink"),
            showlegend=False
        ))
