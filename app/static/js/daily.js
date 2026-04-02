// 오행별 컬러 매핑 (CSS 색상)
const OHAENG_CSS_COLORS = {
    "초록": "#22c55e", "연두": "#84cc16", "청록": "#14b8a6",
    "빨강": "#ef4444", "주황": "#f97316", "분홍": "#ec4899",
    "노랑": "#eab308", "베이지": "#d4a574", "갈색": "#92400e",
    "흰색": "#f1f5f9", "은색": "#cbd5e1", "금색": "#d97706",
    "검정": "#1e293b", "남색": "#1e3a5f", "파랑": "#3b82f6",
};

// 오행별 텍스트 컬러
const OHAENG_TEXT_COLORS = {
    "초록": "#fff", "연두": "#fff", "청록": "#fff",
    "빨강": "#fff", "주황": "#fff", "분홍": "#fff",
    "노랑": "#1e293b", "베이지": "#1e293b", "갈색": "#fff",
    "흰색": "#475569", "은색": "#1e293b", "금색": "#fff",
    "검정": "#fff", "남색": "#fff", "파랑": "#fff",
};

// 오행 한자 매핑
const OHAENG_DISPLAY = {
    "목": "목(木)", "화": "화(火)", "토": "토(土)", "금": "금(金)", "수": "수(水)",
};

// 관계 한글 라벨
const RELATION_LABELS = {
    "생아": "나를 도와주는 날",
    "아생": "에너지를 나누는 날",
    "극아": "도전적인 날",
    "아극": "적극적인 날",
    "비견": "자신감 넘치는 날",
};

// 폼 제출
document.getElementById('daily-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const year = parseInt(document.getElementById('year').value);
    const month = parseInt(document.getElementById('month').value);
    const day = parseInt(document.getElementById('day').value);
    const hourVal = document.getElementById('hour').value;

    if (!year || !month || !day) {
        alert('생년월일을 입력해주세요.');
        return;
    }
    if (hourVal === '') {
        alert('태어난 시간을 선택해주세요.');
        return;
    }

    const hour = parseInt(hourVal);

    document.getElementById('form-section').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    try {
        const res = await fetch('/api/daily', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ year, month, day, hour, minute: 0 })
        });
        const data = await res.json();

        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');

        setTimeout(() => {
            document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

        renderDaily(data);
    } catch (err) {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('form-section').classList.remove('hidden');
        alert('분석에 실패했습니다. 다시 시도해주세요.');
    }
});

function renderDaily(data) {
    // 날짜
    const dateObj = new Date(data.date);
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    document.getElementById('today-date').textContent =
        `${dateObj.getFullYear()}년 ${dateObj.getMonth() + 1}월 ${dateObj.getDate()}일 (${weekdays[dateObj.getDay()]})`;

    // 오늘의 일주
    const tp = data.today_pillar;
    document.getElementById('today-pillar').textContent = `${tp.cheongan}${tp.jiji}`;
    document.getElementById('today-ohaeng-label').textContent =
        `오늘의 기운: ${OHAENG_DISPLAY[tp.ohaeng]} · ${tp.umyang}`;

    // 운세 점수 애니메이션
    const score = data.luck_score;
    const circle = document.getElementById('score-circle');
    const circumference = 2 * Math.PI * 52;
    const offset = circumference - (score / 100) * circumference;

    // 점수에 따른 색상
    let scoreColor = '#3b82f6'; // blue
    if (score >= 80) scoreColor = '#22c55e'; // green
    else if (score >= 60) scoreColor = '#3b82f6'; // blue
    else if (score >= 40) scoreColor = '#f59e0b'; // amber
    else scoreColor = '#ef4444'; // red

    circle.style.stroke = scoreColor;

    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
    }, 100);

    // 점수 카운트업
    const scoreEl = document.getElementById('luck-score');
    let current = 0;
    const step = Math.ceil(score / 30);
    const counter = setInterval(() => {
        current += step;
        if (current >= score) {
            current = score;
            clearInterval(counter);
        }
        scoreEl.textContent = current;
    }, 30);

    // 에너지 설명
    document.getElementById('energy-desc').textContent = data.energy_description;

    // 오늘의 팁
    document.getElementById('daily-tip').textContent = data.daily_tip;

    // 행운의 컬러
    const rec = data.recommendations;
    document.getElementById('lucky-colors').innerHTML = rec.colors.map(color => {
        const bg = OHAENG_CSS_COLORS[color] || '#94a3b8';
        const text = OHAENG_TEXT_COLORS[color] || '#fff';
        return `<span class="px-4 py-2 rounded-full text-sm font-medium shadow-sm"
                    style="background-color: ${bg}; color: ${text}">${color}</span>`;
    }).join('');

    // 행운의 숫자
    document.getElementById('lucky-numbers').innerHTML = rec.numbers.map(num =>
        `<span class="w-12 h-12 md:w-14 md:h-14 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 text-lg md:text-xl font-bold">${num}</span>`
    ).join('');

    // 행운의 방향
    document.getElementById('lucky-direction').textContent = rec.direction;

    // 주의사항
    document.getElementById('caution').textContent = data.caution;

    // 추천 음식
    document.getElementById('lucky-foods').innerHTML = rec.foods.map(food =>
        `<span class="px-3 py-1.5 bg-amber-50 border border-amber-200 rounded-full text-sm text-amber-800">${food}</span>`
    ).join('');

    // 추천 활동
    document.getElementById('lucky-activities').innerHTML = rec.activities.map((act, i) =>
        `<div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl">
            <span class="w-7 h-7 flex items-center justify-center rounded-full bg-blue-500 text-white text-xs font-bold">${i + 1}</span>
            <span class="text-sm text-slate-700">${act}</span>
        </div>`
    ).join('');

    // 내 오행 정보
    document.getElementById('my-ohaeng').textContent = OHAENG_DISPLAY[data.my_ohaeng] || data.my_ohaeng;
    document.getElementById('weakest-ohaeng').textContent = OHAENG_DISPLAY[data.weakest_ohaeng] || data.weakest_ohaeng;
    document.getElementById('relation-label').textContent = RELATION_LABELS[data.relation] || data.relation;
}
