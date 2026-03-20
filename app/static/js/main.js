// 분석 요청 body를 저장 (AI 해석 버튼에서 사용)
let savedRequestBody = null;

// 시간 모름 체크박스 토글
document.getElementById('dont-know-hour').addEventListener('change', (e) => {
    const quiz = document.getElementById('quiz-section');
    const hourInput = document.getElementById('hour');
    if (e.target.checked) {
        quiz.classList.remove('hidden');
        hourInput.disabled = true;
        hourInput.value = '';
        hourInput.classList.add('opacity-50');
    } else {
        quiz.classList.add('hidden');
        hourInput.disabled = false;
        hourInput.classList.remove('opacity-50');
    }
});

// 폼 제출
document.getElementById('analyze-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const year = parseInt(document.getElementById('year').value);
    const month = parseInt(document.getElementById('month').value);
    const day = parseInt(document.getElementById('day').value);
    const bloodType = document.getElementById('blood_type').value || null;
    const dontKnowHour = document.getElementById('dont-know-hour').checked;

    if (!year || !month || !day) {
        alert('생년월일을 입력해주세요.');
        return;
    }

    let hour;

    if (dontKnowHour) {
        document.getElementById('form-section').classList.add('hidden');
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('loading-text').textContent = '시간을 추정하고 있어요...';

        const quizRes = await fetch('/api/estimate-hour', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                year, month, day,
                quiz: {
                    sibling_order: document.getElementById('q-sibling').value,
                    morning_or_night: document.getElementById('q-chronotype').value,
                    first_impression: document.getElementById('q-impression').value,
                    decision_style: document.getElementById('q-decision').value,
                }
            })
        });
        const quizData = await quizRes.json();
        hour = quizData.estimated_hours[0].hour;
    } else {
        hour = parseInt(document.getElementById('hour').value);
        if (isNaN(hour)) {
            alert('태어난 시간을 입력해주세요.');
            return;
        }
    }

    document.getElementById('form-section').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('loading-text').textContent = '운명을 분석하고 있습니다...';

    const body = { year, month, day, hour };
    if (bloodType) body.blood_type = bloodType;
    savedRequestBody = body;

    const analyzeRes = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await analyzeRes.json();

    document.getElementById('loading').classList.add('hidden');
    document.getElementById('results').classList.remove('hidden');

    renderSaju(data.saju);
    renderOhaeng(data.ohaeng);
    renderZodiac(data.zodiac);
    renderChineseZodiac(data.chinese_zodiac);
    renderMBTI(data.predicted_mbti);

    if (data.blood_type) {
        renderBloodType(data.blood_type);
    }

    // 무료 로컬 해석 바로 표시
    if (data.interpretation) {
        renderInterpretation(data.interpretation, 'local-interpretation');
    }
});

function renderInterpretation(interp, targetId) {
    document.getElementById(targetId).innerHTML = `
        <p class="text-lg font-medium text-mystic-100 mb-4">${interp.summary || ''}</p>
        <div class="space-y-4 text-sm text-mystic-200 leading-relaxed">
            ${interp.personality ? `<div><span class="text-mystic-400 font-medium">성격 |</span> ${interp.personality}</div>` : ''}
            ${interp.fortune_2026 ? `<div><span class="text-mystic-400 font-medium">2026년 운세 |</span> ${interp.fortune_2026}</div>` : ''}
            ${interp.love ? `<div><span class="text-mystic-400 font-medium">연애운 |</span> ${interp.love}</div>` : ''}
            ${interp.career ? `<div><span class="text-mystic-400 font-medium">직업운 |</span> ${interp.career}</div>` : ''}
            ${interp.advice ? `<div class="mt-2 p-3 bg-mystic-800/50 rounded-xl text-mystic-100 font-medium">${interp.advice}</div>` : ''}
        </div>
    `;
}

// AI 상세 해석 버튼 클릭
async function requestAIInterpretation() {
    if (!savedRequestBody) return;

    document.getElementById('ai-prompt').classList.add('hidden');
    document.getElementById('ai-loading').classList.remove('hidden');

    try {
        const res = await fetch('/api/analyze/full', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(savedRequestBody)
        });
        const data = await res.json();

        document.getElementById('ai-loading').classList.add('hidden');
        document.getElementById('ai-result').classList.remove('hidden');

        if (data.interpretation && !data.interpretation.error) {
            renderInterpretation(data.interpretation, 'ai-result');
        } else {
            const errMsg = data.interpretation?.error || 'AI 해석을 불러오지 못했어요.';
            document.getElementById('ai-result').innerHTML = `
                <p class="text-mystic-400 text-sm">${errMsg}</p>
            `;
        }
    } catch {
        document.getElementById('ai-loading').classList.add('hidden');
        document.getElementById('ai-result').classList.remove('hidden');
        document.getElementById('ai-result').innerHTML = `
            <p class="text-mystic-400 text-sm">AI 해석 서버에 연결할 수 없습니다.</p>
        `;
    }
}

function renderSaju(saju) {
    const pillars = [
        { name: '년주', ...saju.year_pillar },
        { name: '월주', ...saju.month_pillar },
        { name: '일주', ...saju.day_pillar },
        { name: '시주', ...saju.hour_pillar },
    ];

    const colors = ['from-blue-500 to-cyan-500', 'from-green-500 to-emerald-500', 'from-amber-500 to-yellow-500', 'from-pink-500 to-rose-500'];

    document.getElementById('saju-pillars').innerHTML = pillars.map((p, i) => `
        <div class="bg-mystic-800 rounded-xl p-4 border border-mystic-600/30">
            <div class="text-xs text-mystic-400 mb-2">${p.name}</div>
            <div class="text-2xl font-bold bg-gradient-to-b ${colors[i]} bg-clip-text text-transparent">
                ${p.cheongan}${p.jiji}
            </div>
        </div>
    `).join('');

    document.getElementById('saju-animal').textContent = `${saju.animal}띠`;
}

function renderOhaeng(ohaeng) {
    const elements = [
        { name: '목(木)', key: '목', color: 'bg-green-500' },
        { name: '화(火)', key: '화', color: 'bg-red-500' },
        { name: '토(土)', key: '토', color: 'bg-yellow-600' },
        { name: '금(金)', key: '금', color: 'bg-gray-300' },
        { name: '수(水)', key: '수', color: 'bg-blue-500' },
    ];

    const maxCount = Math.max(...Object.values(ohaeng.counts), 1);

    document.getElementById('ohaeng-chart').innerHTML = elements.map(el => {
        const count = ohaeng.counts[el.key];
        const pct = (count / maxCount) * 100;
        return `
            <div class="flex items-center gap-3">
                <span class="w-14 text-sm text-mystic-300">${el.name}</span>
                <div class="flex-1 bg-mystic-800 rounded-full h-6 overflow-hidden">
                    <div class="${el.color} h-full rounded-full transition-all duration-700 flex items-center justify-end pr-2"
                         style="width: ${Math.max(pct, 8)}%">
                        <span class="text-xs font-bold text-white">${count}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    document.getElementById('ohaeng-summary').textContent =
        `내 오행: ${ohaeng.my_ohaeng} | 가장 강한 오행: ${ohaeng.strongest} | 가장 약한 오행: ${ohaeng.weakest}`;
}

function renderZodiac(zodiac) {
    document.getElementById('zodiac-result').innerHTML = `
        <div class="flex items-center gap-4 mb-3">
            <span class="text-3xl font-bold text-mystic-100">${zodiac.sign}</span>
            <span class="text-sm px-3 py-1 bg-mystic-800 rounded-full text-mystic-300">${zodiac.element} / ${zodiac.ruling_planet}</span>
        </div>
        <p class="text-mystic-300 text-sm mb-3">${zodiac.personality}</p>
        <div class="flex flex-wrap gap-2">
            ${zodiac.keywords.map(k => `<span class="px-3 py-1 bg-mystic-800/80 rounded-full text-xs text-mystic-200">${k}</span>`).join('')}
        </div>
    `;
}

function renderBloodType(bt) {
    document.getElementById('blood-type-section').classList.remove('hidden');
    document.getElementById('blood-type-result').innerHTML = `
        <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl font-bold text-red-400">${bt.type}형</span>
        </div>
        <p class="text-mystic-300 text-sm mb-3">${bt.personality}</p>
        <div class="grid grid-cols-2 gap-3 text-sm">
            <div>
                <span class="text-mystic-400 text-xs">장점</span>
                <div class="flex flex-wrap gap-1 mt-1">
                    ${bt.strengths.map(s => `<span class="px-2 py-0.5 bg-green-900/40 rounded text-green-300 text-xs">${s}</span>`).join('')}
                </div>
            </div>
            <div>
                <span class="text-mystic-400 text-xs">단점</span>
                <div class="flex flex-wrap gap-1 mt-1">
                    ${bt.weaknesses.map(w => `<span class="px-2 py-0.5 bg-red-900/40 rounded text-red-300 text-xs">${w}</span>`).join('')}
                </div>
            </div>
        </div>
        <p class="mt-3 text-sm text-mystic-300"><span class="text-mystic-400">연애 스타일:</span> ${bt.love_style}</p>
    `;
}

function renderChineseZodiac(cz) {
    document.getElementById('zodiac-cn-result').innerHTML = `
        <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl font-bold text-amber-400">${cz.animal}띠</span>
        </div>
        <p class="text-mystic-300 text-sm mb-3">${cz.personality}</p>
        <div class="flex flex-wrap gap-2 mb-3">
            ${cz.traits.map(t => `<span class="px-3 py-1 bg-mystic-800/80 rounded-full text-xs text-mystic-200">${t}</span>`).join('')}
        </div>
        <div class="grid grid-cols-2 gap-3 text-sm">
            <div>
                <span class="text-mystic-400 text-xs">잘 맞는 띠</span>
                <p class="text-green-300 mt-1">${cz.compatible.join(', ')}</p>
            </div>
            <div>
                <span class="text-mystic-400 text-xs">안 맞는 띠</span>
                <p class="text-red-300 mt-1">${cz.incompatible.join(', ')}</p>
            </div>
        </div>
        <p class="mt-3 text-sm text-mystic-300"><span class="text-mystic-400">2026년 운세:</span> ${cz.fortune_2026}</p>
    `;
}

function renderMBTI(mbti) {
    const axes = [
        { key: 'E_I', labels: ['E 외향', 'I 내향'], colors: ['bg-amber-500', 'bg-blue-500'] },
        { key: 'S_N', labels: ['S 감각', 'N 직관'], colors: ['bg-green-500', 'bg-purple-500'] },
        { key: 'T_F', labels: ['T 사고', 'F 감정'], colors: ['bg-cyan-500', 'bg-pink-500'] },
        { key: 'J_P', labels: ['J 판단', 'P 인식'], colors: ['bg-red-500', 'bg-teal-500'] },
    ];

    document.getElementById('mbti-result').innerHTML = `
        <div class="text-center mb-5">
            <span class="text-4xl font-bold tracking-wider bg-gradient-to-r from-mystic-300 to-pink-300 bg-clip-text text-transparent">${mbti.type}</span>
        </div>
        <div class="space-y-3">
            ${axes.map(axis => {
                const scores = mbti.scores[axis.key];
                const letters = Object.keys(scores);
                const left = scores[letters[0]];
                const right = scores[letters[1]];
                return `
                    <div>
                        <div class="flex justify-between text-xs text-mystic-400 mb-1">
                            <span>${axis.labels[0]}</span>
                            <span>${axis.labels[1]}</span>
                        </div>
                        <div class="flex h-5 rounded-full overflow-hidden bg-mystic-800">
                            <div class="${axis.colors[0]} flex items-center justify-center text-xs font-bold" style="width:${left}%">${left}%</div>
                            <div class="${axis.colors[1]} flex items-center justify-center text-xs font-bold" style="width:${right}%">${right}%</div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}
