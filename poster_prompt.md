# 포스터 제작 요청 — 1단계: 내용 (StrongARM 비교기 Sizing 연구)

이 요청은 `C:\Japan` 저장소에서 작업하는 Claude에게 주는 것이다. 이번 단계에서는 **내용만** 다룬다. 색, 폰트, 아이콘, 장식 같은 디자인은 다음 단계에서 따로 요청한다. 양식에 이미 있는 스타일은 그대로 두고, 새로 다듬지 말 것.

## 0. 시작 전에 확인할 것

빈칸이 있으면 작업을 시작하기 전에 먼저 물어볼 것. 괄호 안은 답이 없을 때 쓸 기본값이다.

| 항목 | 값 |
|---|---|
| 저자 | (논문 저자 6명을 논문 순서대로. 영문: Dongui Hong, Min Kim, Doohyeong Kim, Sangyun Kim, Wooeun Choi, Yunjae Lee / 한글: 홍동의, 김민, 김두형, 김상윤, 최우은, 이윤재) |
| 남인호, 백광현 교수님을 저자에 넣을지 (IEIE 양식의 이전 포스터에는 들어 있었음) | (넣지 않음. 논문 저자만) |
| 성과교류회 인쇄 크기 | (IEIE 양식 크기 그대로 59.4 × 84.1 cm) |
| 사업단 배너 양식(`반도체특성화대학사업단 출품 양식.pptx`)도 써야 하는지 | (쓰지 않음) |
| ICEIC 게시 형식: A0 1장 또는 A4 가로 12장 | (A0 1장) |
| Baseline과 개선 회로의 레이아웃 캡처 파일 | (없으면 자리만 표시) |
| Timeout·Invalid 발생 횟수를 넣을지 | (넣지 않음. 최종 논문에서 뺀 내용) |

## 1. 목표

같은 연구 주제로 포스터 두 장을 만든다.

1. **ICEIC 2027** (일본 개최, 영어): 이번에 쓴 ICEIC 2027 논문 영문 최종본을 기준으로 한다.
2. **2026 반도체 특성화대학사업단 성과교류회** (반전트, 한국어): 같은 내용을 한글 논문 기준으로 만든다. 양식은 IEIE 2026 Summer 포스터 양식을 바탕으로 한다.

두 포스터는 **블록 구성과 수치가 같고 언어만 다르다.** 그래서 먼저 마스터 원고(한/영)를 만들고, 그다음 각 규격에 맞춘 배치 초안을 만든다.

## 2. 양식과 규격

| 발표 | 기반 양식 | 크기 | 언어 |
|---|---|---|---|
| 성과교류회 (반전트) | `2026 ieie 2026 SUMMER_poster_template_사사추가.pptx` | 59.4 × 84.1 cm (A1 세로) | 한국어 |
| ICEIC 2027 | 위와 같은 양식의 배치를 A0로 확대 | 84.1 × 118.9 cm (A0 세로) | 영어 |

- **IEIE 양식의 구조**
  - 위쪽 헤더 상자(0.4–14.4 cm): 왼쪽 위 CAU 로고, 오른쪽 위 IEIE 로고, 제목(60 pt), 저자(32 pt), 소속
  - 그 아래 두 단(각 약 28.8 cm 폭)에 회색 머리띠가 달린 섹션 상자가 있다. 섹션 제목은 36 pt, 본문은 24 pt이고 글꼴은 Times New Roman이다.
  - 기존 섹션: Abstract, Introduction, 회로 설계 및 parameter optimization (Fig. 1 포함), Result, Acknowledgement
- **양식 안의 기존 내용은 전부 교체한다.** 지금 들어 있는 것은 우리 팀의 이전 연구다(6-bit SAR ADC, Bootstrapped Switch, ICMR 최적화). 새 포스터에 이전 연구의 문장, 수치, 그림이 하나도 남으면 안 된다.
- **A0는 A1의 정확히 √2배다.** 그래서 ICEIC판은 성과교류회판의 위치와 글자 크기를 모두 1.414배 하면 같은 배치가 된다.
- **ICEIC 게시판의 "Paper Information"은 학회가 붙여 주는 것**으로 보이니 포스터에는 넣지 않는다(`poster_가이드.png`).

## 3. 근거 자료: 여기 있는 것만 쓸 것

| 자료 | 경로 | 비고 |
|---|---|---|
| 논문 최종본 (영문) | `ICEIC2027_English_2pages_v2_final.doc` | ICEIC판의 기준. 문장, 수치, 용어의 최종 기준 |
| 논문 (한글) | `ICEIC2027_Korean_2pages_v2.doc` | 성과교류회판의 기준. 영문 final보다 이전 버전일 수 있다. 수치나 내용이 다르면 영문 final을 따르고, 어디가 달랐는지 보고할 것 |
| 논문 구성안 | `논문 구성안.md`, `README.md` | 지면 때문에 논문에서 뺀 세부 내용 (사양 수치, 시뮬레이션 조건) |
| Fig. 1 회로도 | `ICEIC2027_Korean_2pages_WordFixed_우은버전.docx` 안의 `word/media/image2.png` | 손으로 그린 StrongARM Core 회로도. Cadence 캡처(`image1.png`)는 쓰지 않는다 |
| Fig. 2 Sizing 민감도 | `sim_result/results/fig2/fig2_sizing_sensitivity_en.png`, `_ko.png` | 데이터 `fig2_data.csv`, 생성 스크립트 `sim_result/fig2_sizing_sensitivity.py` |
| 개별 Sweep 원자료 | `sim_result/results/size_sweep/`, `sim_result/sizing_sweep_results.md` | |
| Pre-/Post-Layout 결과 | `sim_result/results/{baseline, candidate, baseline_post_layout, post_layout_4.8u_8u}/` | `*_cdf_summary.csv`, `*_overview.png` |

주의할 점:

- 숫자는 기억이나 이 프롬프트를 믿지 말고 위의 CSV와 논문에서 다시 읽어서 확인할 것.
- Sweep의 Baseline 값과 Table I의 Pre-Layout Baseline 값은 서로 다른 시뮬레이션 실행 결과다. 두 값을 한 표에 섞지 말고, 변화율은 각 데이터의 Baseline을 기준으로 쓸 것.
  - Sweep (`fig2_data.csv`): σ 207.159 μV, 지연 2.13689 ns, 에너지 28.6297 pJ
  - Table I Pre-Layout: σ 206.440 μV, 지연 2.1366 ns, 에너지 28.646 pJ
- `*_overview.png`는 확인용 그림이라 축 이름이 "CSV units"로 되어 있다. 포스터에 쓰려면 다시 그려야 한다. 쓰기로 했다면 "재작성 필요 그림" 목록에만 올리고, 이번 단계에서 다시 그리지는 않는다.
- 레이아웃 캡처와 SR Latch 회로도는 저장소에 없다. 0번 표에 파일이 없으면 자리만 표시한다.

## 4. 포스터 구성: IEIE 양식의 섹션 상자에 맞춰 배치

논문의 흐름(사양 → 회로 → 그룹별 Sizing 분석 → 개선 회로 선정 → Pre-/Post-Layout 비교 → 결론)을 따른다. 다만 2페이지 논문에서 지면 때문에 뺀 세부 내용은 포스터에서 살린다.

배치 기본안은 양식의 두 단 구조를 그대로 쓰는 것이다.

- 왼쪽 단: ②–④
- 오른쪽 단: ⑤–⑨

블록마다 들어가야 할 내용이 다 들어가는 한, 섹션 상자는 늘리거나 줄이거나 새로 만들어도 된다. 섹션 제목은 양식처럼 Abstract, Introduction, Conclusion, Acknowledgement, References는 영어로 쓰고, 내용 섹션은 각 언어로 쓴다.

1. **헤더**
   - 제목은 논문 제목을 그대로 쓴다.
     - 영: "Sensitivity-Guided Transistor Sizing and Post-Layout Verification of a StrongARM Comparator for 10-bit SAR ADC Applications"
     - 한: "10-bit SAR ADC용 StrongARM 비교기의 민감도 기반 트랜지스터 크기 선정 및 레이아웃 후 검증"
   - 저자와 소속: 0번 표 기준. 소속은 양식의 "School of Electrical and Electronics Engineering, Chung-Ang University, Seoul, Korea"를 그대로 쓴다.
2. **Abstract**
   - 논문 초록을 3–4문장으로 줄인다. 핵심 수치(Post-Layout 지연 −17.77%, 에너지 −40.76%)는 꼭 넣는다.
3. **Introduction** (bullet 3개 이내)
   - SAR ADC에서 비교기가 하는 역할
   - StrongARM 비교기의 특징
   - 트랜지스터 크기에 따른 잡음·지연·에너지 Trade-off [1]–[3]
   - 이 연구에서 한 일
4. **회로 설계 및 평가 방법** (영: Circuit Design and Evaluation Method)
   - **설계 사양 표**
     - 공정과 전압: 500-nm CMOS, VDD 5 V, VCM 2.5 V
     - ADC 조건: 10-bit, 차동 Full-scale 2.5 V, 1 LSB = 2.441 mV
     - 정확도 목표: 판정 중심 |μ| ≤ 0.5 LSB (1.221 mV), 입력 환산 잡음 σ ≤ 0.1 LSB (244.14 μV RMS)
     - Timing: 80-MHz Clock, 5-ns 판정 마감
     - 해상도는 [4]를 참고했고, 입력 범위·잡음·Timing 예산은 자체 설정했다는 점을 밝힐 것.
   - **Fig. 1 회로도와 Sizing 그룹 표** (그룹 / 소자 / Baseline W)
     - 그룹과 소자의 대응은 아래와 같다. 채널 길이 L은 모두 0.5 μm로 고정이다. 이 대응은 Cadence 캡처(`image1.png`)로 한 번 더 확인할 것.

       | 그룹 | 소자 | Baseline W |
       |---|---|---|
       | Input Pair | M1·M2 | 6.4 μm |
       | Tail NMOS | M7 | 3.2 μm |
       | NMOS Latch | M3·M4 | 3.2 μm |
       | PMOS Latch | M5·M6 | 1.6 μm |
       | Reset | S1–S4 | 3.2 μm |

     - 회로도 위에 그룹을 표시하는 건 디자인 단계 메모로만 남긴다.
   - **평가 방법**
     - 흐름도 한 줄: Baseline → 그룹별 개별 Sweep (15개 조건) → 개선 회로 선정 → Pre-Layout → Layout·PEX → Post-Layout
     - Transient Noise 시뮬레이션: Vdiff −1.2 ~ +1.2 mV 범위 40개 지점, 지점마다 100회 비교
     - μ와 σ 추출: P(High) = Φ[(Vdiff − μ)/σ]로 피팅
     - 지연: Clock 상승 에지부터 내부 판정 완료까지
     - 비교당 에너지: 한 Clock 주기의 평균 공급 전력 × 주기
     - 지연과 에너지는 40개 지점의 산술평균이다.
5. **Sizing 민감도 분석** (영: Transistor Sizing Sensitivity, 핵심 블록이므로 면적을 가장 크게)
   - Fig. 2와 함께 대표 조건 표를 넣는다. 값은 `fig2_data.csv`에서 다시 확인할 것.

     | 변경 (μm) | 잡음 | 평균 지연 | 에너지 |
     |---|---|---|---|
     | Input Pair 6.4→8.0 | −9.1% | −4.9% | −7.5% |
     | Tail NMOS 3.2→1.6 | −23.4% | +15.4% | −27.1% |
     | NMOS Latch 3.2→1.6 | +18.5% | +26.1% | +13.0% |
     | PMOS Latch 1.6→4.8 | +4.9% | −27.4% | −49.2% |
     | Reset 3.2→4.8 | −5.4% | +3.6% | +0.3% |

   - 해석은 3–4줄로 쓴다.
     - PMOS Latch를 넓히면 지연과 에너지가 크게 줄고, 잡음은 조금 늘어난다.
     - Tail NMOS를 줄이면 잡음·에너지와 지연 사이에 Trade-off가 생긴다.
     - Input Pair를 넓히면 세 지표가 모두 좋아진다.
     - Reset은 영향이 작다.
     - 결론: 그래서 Input Pair와 PMOS Latch를 Sizing 대상으로 골랐다.
6. **개선 회로 및 Post-Layout 검증** (영: Improved Design and Post-Layout Verification)
   - **Pre-Layout**
     - 변경: Input Pair 6.4→8.0 μm, PMOS Latch 1.6→4.8 μm, 나머지 그룹은 Baseline
     - 결과: 평균 지연 −31.11%, 에너지 −50.42%, μ와 σ 모두 목표 만족
   - **Post-Layout**
     - Baseline과 개선 회로의 레이아웃 캡처(0번 표), PEX 수행 사실, 두 회로가 같은 SR Latch Schematic을 썼다는 점
     - Table I 전체 (논문 그대로)
     - 핵심 결과: 평균 지연 −17.77%, 에너지 −40.76%, μ와 σ 모두 목표 만족
   - **한계:** 일부 입력 조건에서 5 ns 안에 판정이 끝나지 않아, 모든 조건에서 Timing을 만족한다고는 할 수 없다. Timeout·Invalid 횟수는 0번 표에서 넣기로 한 경우에만 쓴다.
   - Pre/Post 지연·에너지 감소율 네 개는 크게 강조할 후보로 표시한다.
7. **Conclusion**
   - 논문 결론 3문장을 bullet 3개로 바꾼다.
8. **Acknowledgement**
   - 양식에 있는 KIAT 사사 문구를 그대로 둔다(논문 사사와 같은 과제 번호 P0030093).
9. **References** (작은 글씨)
   - 논문의 [1]–[4]를 그대로 쓴다. 양식에는 이 상자가 없으니 Acknowledgement 근처에 작게 추가한다.

## 5. 작성 규칙

- **논문과 일치:** 수치와 용어가 논문 최종본과 어긋나면 안 된다. 논문에 없는 결론, 주장, 향후 계획을 새로 만들지 말 것. 포스터에서 살리는 세부 내용(사양, 시뮬레이션 조건)도 3번 근거 자료에 있는 것만 쓴다.
- **글의 양:** 이전 포스터처럼 긴 문단을 이어 붙이지 말 것. 블록마다 짧은 문장이나 bullet 3–5개로 쓰고, 면적의 절반 이상은 그림과 표에 쓴다. 핵심 수치는 굵게 표시해서 디자인 단계에서 강조할 수 있게 한다.
- **분량:** 본문(헤더와 참고문헌 제외)은 영문 500–700 단어, 한글도 비슷한 분량으로. 양식의 본문 24 pt(A0판은 34 pt)로 넣었을 때 넘치면 블록마다 무엇을 줄일지 제안할 것.
- **용어 통일:** "Baseline / 개선 회로 (Improved circuit)"로 통일한다. Fig. 2 범례의 "candidate"는 이와 맞지 않으므로 재작성 필요 그림 목록에 올린다.
- **단위 표기:** μm, μV RMS, ns, pJ를 쓰고 숫자와 단위 사이는 띄운다. "5-ns 판정 마감"처럼 수식어로 쓸 때는 하이픈을 넣는다.
- **한/영 원고:** 블록 구조와 수치를 똑같이 맞춘다. 한글판의 소자와 지표 이름은 논문 한글판 표기(Input Pair, PMOS Latch, 판정 중심, 입력 환산 잡음, 비교당 에너지)를 따른다.

## 6. 산출물과 진행 순서

두 포스터 중 하나만 먼저 요청할 수도 있다. 그럴 때는 요청받은 판의 원고와 초안만 만든다. 블록 이름과 순서는 4번을 그대로 따라서, 나머지 판을 나중에 같은 구조로 추가할 수 있게 한다.

**A. 마스터 원고. 다 만들면 여기서 멈추고 내 확인을 받을 것**

- `poster/poster_content.md` 파일 하나에 아래 내용을 담는다.
  - 블록별 한/영 원고 (한 판만 요청받았으면 그 언어만)
  - 블록마다 들어갈 그림·표와 캡션
  - 왼쪽 단, 오른쪽 단 배치와 블록별 권장 높이 비율
  - 단어 수
  - 맨 아래에 "확인 필요 사항" 목록과 "재작성 필요 그림" 목록

**B. 내가 확인한 뒤에 만들 배치 초안**

- **공통**
  - IEIE 양식 복사본의 섹션 상자에 원고, 그림, 표를 넣는다.
  - 헤더 상자, 로고, 섹션 상자 모양, 글꼴, 글자 크기 비율은 양식 그대로 둔다.
  - 상자 위치와 크기만 내용에 맞게 조정한다.
  - 두 판 중 나중에 만드는 판은 먼저 만든 판의 배치를 √2배 또는 1/√2배로 맞춘다.
- **`poster/poster_draft_ko.pptx`** (성과교류회, 59.4 × 84.1 cm)
  - 양식 원래 크기 그대로 쓴다.
- **`poster/poster_draft_en.pptx`** (ICEIC, 84.1 × 118.9 cm)
  - 양식의 모든 위치, 크기, 글자 크기를 √2배로 키운 뒤 영어 원고를 넣는다.
  - 글자 크기는 본문 24→34 pt, 섹션 제목 36→51 pt, 제목 60→85 pt, 저자 32→45 pt가 된다.
- **렌더링 확인**
  - PowerPoint로 PNG를 렌더링해서 글자 넘침, 겹침, 이전 연구 내용이 남아 있지 않은지 직접 확인한다.
  - 슬라이드 텍스트에서 "6-bit", "Bootstrapped", "ICMR", "pedestal", "10 MS/s"를 검색해서 하나도 안 나와야 한다.
  - 안 들어가는 블록이 있으면 줄일 문장을 제안한다.

## 7. 하지 말 것

- 원본 양식이나 논문 파일을 덮어쓰지 말 것. 반드시 복사본에서 작업한다.
- 색, 폰트, 아이콘, 장식을 새로 정하지 말 것. 다음 단계에서 한다.
- 그림을 새로 그리거나 시뮬레이션을 다시 돌리지 말 것. 필요하면 목록으로 제안만 한다.
