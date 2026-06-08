"""S07 (상태&묘사 211개)를 3개로 분리"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from collections import Counter

final = json.loads(Path('scenario_tags_final.json').read_text(encoding='utf-8'))
tagged = dict(final['tagged'])

# ── 3개 새 카테고리 정의 ────────────────────────────────────────────────────────
NEW_SCENARIOS = [
    {
        'id': 'S07a', 'ko': '🎨 색깔 & 외모', 'en': 'Colors & Appearance',
        'color': '#f472b6',
        'words': [
            # 색깔 명사
            '색','색깔','갈색','검은색','검정','까만색','노란색','녹색','보라색',
            '분홍색','빨간색','초록색','파란색','하얀색','흰색','회색','주황색',
            # 색깔 형용사
            '노랗다','까맣다','빨갛다','파랗다','하얗다','푸르다','붉다',
            # 외모/모양 형용사
            '날씬하다','뚱뚱하다','화려하다','못생기다','새롭다','밝다','어둡다',
            '깨끗하다','깨끗이','더럽다','부드럽다','두껍다','얇다','굵다','진하다',
            # 외모 명사
            '디자인','모양','모습','유행','인기','유명',
        ]
    },
    {
        'id': 'S07b', 'ko': '📏 크기 & 비교', 'en': 'Size & Comparison',
        'color': '#38bdf8',
        'words': [
            # 크기 형용사
            '길다','짧다','높다','낮다','넓다','좁다','깊다','많다','적다',
            '무겁다','가볍다','강하다','약하다','충분하다','가득',
            # 크기/측정 명사
            '크기','높이','길이','무게','속도','정도','수','영하','이상','반',
            # 비교 형용사
            '같다','다르다','비슷하다','똑같다','낫다','멀다','이르다',
            # 정도 부사
            '가장','거의','더','매우','무척','전부','제일','조금씩','훨씬',
            '열심히','따로','각각','오래',
            # 수량/범위
            '두','두세','서너','스무','한두','한','모두','모든','대부분',
            '전체','부분','일부','다양','며칠',
        ]
    },
    {
        'id': 'S07c', 'ko': '🧠 성격 & 특성', 'en': 'Personality & Traits',
        'color': '#a78bfa',
        'words': [
            # 성격 형용사
            '게으르다','괜찮다','궁금하다','귀찮다','급하다','나쁘다','늦다',
            '복잡하다','부지런하다','분명하다','소중하다','시끄럽다','심하다',
            '쌀쌀하다','알맞다','어리다','익숙하다','적당하다','젊다',
            '조용하다','착하다','특별하다','튼튼하다','훌륭하다','힘들다',
            '간단하다','아니다','어떠하다','어떤','어떻다','이렇다','이런',
            '저렇다','저런','그렇다','그런','낫다',
            # 성격 명사
            '성격','태도','분위기','습관','버릇','능력','경험','나이','연세',
            '수고','방법','규칙','목적','결과',
            # 추상 개념 명사
            '뜻','의미','내용','종류','중심','정확','최고','단순',
            '편리','편안','금지','소리','냄새','지방','줄','차례',
            '아무것','오래간만','오랜만','오랫동안','고등학생','아주머니',
            '매년','매달','매주','해마다','현재','서양','꽃집','반바지',
            # 기타
            '무슨','어느','다른','옛','첫','보통','다','다하다',
            '비다','불다','세다','흐르다','적다','짜다','부르다',
            '여러분','청소','흰색',
        ]
    },
]

# ── 미배정 처리: 더 정확한 카테고리로 이동 ──────────────────────────────────────
MANUAL_FIXES = {
    # 정도 부사 → S07b
    '너무': 'S07b', '약간': 'S07b',
    # 연결어&부사 → S16
    '특히': 'S16', '주로': 'S16',
    # 장소 → S04
    '독일': 'S04',
    # 음식 맛 → S10
    '시다': 'S10', '싱겁다': 'S10',
    # 성격 → S07c
    '것': 'S07c', '똑똑하다': 'S07c', '부족': 'S07c',
    '오래되다': 'S07c', '중요': 'S07c', '처음': 'S07c',
}

# 분리 적용
s07_set = {w for w, sid in tagged.items() if sid == 'S07'}
assigned = set()

for new_s in NEW_SCENARIOS:
    for w in new_s['words']:
        if w in s07_set:
            tagged[w] = new_s['id']
            assigned.add(w)

# 미배정 수동 처리
remaining = s07_set - assigned
for w in remaining:
    tagged[w] = MANUAL_FIXES.get(w, 'S07c')

# 결과 집계
counts = Counter(tagged.values())
print('\n=== S07 분리 결과 ===')
for s in NEW_SCENARIOS:
    print(f"  {s['ko']:20} ({s['id']}): {counts.get(s['id'],0):3}개")
print(f"  S07 잔여:                   {counts.get('S07',0):3}개  ← 0이어야 함")

# 시나리오 목록 업데이트
old_scenarios = final['scenarios']
new_scenario_list = []
for s in old_scenarios:
    if s['id'] == 'S07':
        # S07을 3개로 교체
        for ns in NEW_SCENARIOS:
            new_scenario_list.append({'id':ns['id'],'ko':ns['ko'],'en':ns['en'],'color':ns['color']})
    else:
        new_scenario_list.append(s)

out = {'tagged': tagged, 'scenarios': new_scenario_list}
Path('scenario_tags_v2.json').write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

print('\n=== 전체 시나리오 최종 ===')
counts2 = Counter(tagged.values())
sid_names = {s['id']: s['ko'] for s in new_scenario_list}
sid_names['NUM'] = '🔢 숫자 & 단위'
for s in new_scenario_list + [{'id':'NUM','ko':'🔢 숫자 & 단위'}]:
    n = counts2.get(s['id'], 0)
    if n:
        print(f"  {s['ko']:25} ({s['id']}): {n:3}개")

print(f"\n  총합: {sum(counts2.values())}개")
print('\n✅ scenario_tags_v2.json 저장 완료')
