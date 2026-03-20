document.getElementById('compat-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const getValue = (id) => {
        const val = document.getElementById(id).value;
        return val ? parseInt(val) : null;
    };

    const p1 = {
        year: getValue('p1-year'),
        month: getValue('p1-month'),
        day: getValue('p1-day'),
        hour: getValue('p1-hour'),
    };
    const p2 = {
        year: getValue('p2-year'),
        month: getValue('p2-month'),
        day: getValue('p2-day'),
        hour: getValue('p2-hour'),
    };

    if (!p1.year || !p1.month || !p1.day || p1.hour === null ||
        !p2.year || !p2.month || !p2.day || p2.hour === null) {
        alert('두 사람의 생년월일시를 모두 입력해주세요.');
        return;
    }

    const p1Blood = document.getElementById('p1-blood').value;
    const p2Blood = document.getElementById('p2-blood').value;
    if (p1Blood) p1.blood_type = p1Blood;
    if (p2Blood) p2.blood_type = p2Blood;

    document.getElementById('form-section').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    try {
        const res = await fetch('/api/compatibility', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ person1: p1, person2: p2 })
        });
        const data = await res.json();

        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');

        // 종합 점수
        document.getElementById('total-score').textContent = data.score;
        setTimeout(() => {
            document.querySelector('#score-bar > div').style.width = data.score + '%';
        }, 100);

        // 상세 점수
        const details = [
            { label: '사주 궁합', data: data.details.saju_compatibility, color: 'bg-purple-500' },
            { label: '별자리 궁합', data: data.details.zodiac_compatibility, color: 'bg-blue-500' },
            { label: '띠 궁합', data: data.details.chinese_zodiac_compatibility, color: 'bg-amber-500' },
            { label: '혈액형 궁합', data: data.details.blood_type_compatibility, color: 'bg-red-500' },
        ];

        document.getElementById('detail-scores').innerHTML = details.map(d => {
            const score = d.data.score;
            if (score === null) return '';
            return `
                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="text-mystic-300">${d.label}</span>
                        <span class="text-mystic-200 font-medium">${score}점</span>
                    </div>
                    <div class="h-4 bg-mystic-800 rounded-full overflow-hidden">
                        <div class="${d.color} h-full rounded-full transition-all duration-700" style="width:${score}%"></div>
                    </div>
                    <p class="text-xs text-mystic-500 mt-1">${d.data.comment}</p>
                </div>
            `;
        }).join('');

        // AI 해석
        document.getElementById('ai-summary').textContent = data.summary || '궁합 해석을 불러올 수 없습니다.';

    } catch (err) {
        document.getElementById('loading').classList.add('hidden');
        alert('분석 중 오류가 발생했습니다.');
        location.reload();
    }
});
