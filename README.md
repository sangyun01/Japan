# ICEIC 2027 논문 구성안 (2페이지)

제목(안): Sensitivity-Guided Transistor Sizing and Post-Layout Verification of a StrongARM Comparator for SAR ADC Applications

핵심 흐름: SAR ADC 응용 사양 설정 → StrongARM 설계 → 개별 Sizing 분석 → Candidate 선정 및 성능 개선 → Layout·PEX 검증

[실측]은 확보한 결과, [측정 예정]은 아직 수행하지 않은 Candidate Post-Layout 결과를 의미함.

# Page 1 — 연구 배경 및 설계

## Abstract

- 10-bit SAR ADC 응용을 위한 StrongARM Comparator 설계 및 Transistor Sizing 분석.
- 500 nm CMOS에서 5개 주요 소자 그룹의 Noise·Delay·Energy 민감도 평가.
- 분석 결과를 바탕으로 Input Pair 및 PMOS Latch Width를 조합한 Candidate 설계.
- [실측] Candidate의 Pre-Layout Noise 2.40%, 평균 Delay 31.11%, Energy 50.42% 감소.
- [측정 예정] Baseline과 Candidate의 Post-Layout 성능 비교를 통한 개선 효과 검증.

## I. Introduction

문단 1 — 연구 배경

- SAR ADC에서 Comparator는 각 비트 판정의 정확도와 속도를 결정하는 주요 회로임.
- StrongARM Latch는 정적 전력 소비가 없는 동적 비교기로 SAR ADC에 활용됨 [1], [2].
- Comparator의 Noise, Offset, Delay 및 Energy는 소자 크기에 영향을 받음 [2], [3].

문단 2 — 연구 목적

- 주요 트랜지스터 그룹별 Sizing에 따른 성능 민감도와 Trade-off 분석.
- 개별 분석 결과를 활용하여 성능 개선용 Candidate 설계.
- Candidate의 Pre-Layout 성능 검증 및 Baseline과의 Post-Layout 비교.
- 10-bit, 1-MS/s SAR ADC 응용 가정은 기존 구현 사례 [4] 참고.

## II. Circuit Design and Specifications

문단 1 — 설계 환경 및 요구 사양

- 500 nm CMOS, \\(V\_{DD}=5\\) V, \\(V\_{CM}=2.5\\) V.
- 10-bit, 1-MS/s SAR ADC 응용 가정, 차동 Full-scale = 2.5 V.
- 1 LSB = 2.441 mV.
- Nominal Decision Center 목표: \\(|\mu|\leq1.221\\) mV (0.5 LSB).
- Input-referred Noise 목표: \\(\sigma\leq244.14\\) µV RMS (0.1 LSB).
- 80 MHz Comparator 시험 Clock에서 내부 판정 마감 시간 5 ns 설정.
- 응용 해상도·속도는 [4] 참고, Full-scale 및 정확도·타이밍 기준은 본 연구에서 설정.

문단 2 — StrongARM 회로 구성

- StrongARM Core와 출력 유지를 위한 SR Latch 구성.
- Input Pair, Tail NMOS, Cross-coupled NMOS/PMOS, Reset Transistors로 구분.
- Channel Length를 고정하고 Width를 변경하여 성능 분석.
- Baseline Width: Input 6.4, Tail 3.2, NMOS Latch 3.2, PMOS Latch 1.6, Reset 3.2 µm.

Fig. 1. StrongARM Comparator Schematic

- 실제 StrongARM + SR Latch 회로도.
- 5개 Sizing 그룹 표시.
- Candidate에서 변경하는 Input Pair와 PMOS Latch 강조.

문단 3 — 시뮬레이션 및 평가 방법

- DIFF = −1.2\~+1.2 mV, 40개 지점, 각 지점에서 100회 판정.
- Gaussian CDF 피팅으로 \\(\mu\\), \\(\sigma\\) 추출.
- Internal Decision Delay와 공급 전력 기반 Energy/Comparison 측정.
- Delay·Energy는 40개 DIFF 지점의 동일 가중치 산술평균 사용.

# Page 2 — 분석, Candidate 및 구현 검증

## III. Simulation Results and Discussion

### A. Transistor Sizing Sensitivity Analysis

문단 1 — 개별 Sizing 실험

- 5개 소자 그룹의 Width를 각각 독립적으로 변경.
- 그룹별 3개 Width, 총 15개 시뮬레이션 조건.
- 다른 소자는 Baseline으로 고정하여 성능 변화 비교.

문단 2 — 주요 결과 [실측]

| 변경 조건                   | Noise 변화 | Delay 변화 | Energy 변화 |
| ----------------------- | -------- | -------- | --------- |
| Input 6.4 → 8.0 µm      | −9.1%    | −4.9%    | −7.5%     |
| Tail 3.2 → 1.6 µm       | −23.4%   | +15.4%   | −27.1%    |
| NMOS Latch 3.2 → 1.6 µm | +18.5%   | +26.1%   | +13.0%    |
| PMOS Latch 1.6 → 4.8 µm | +4.9%    | −27.4%   | −49.2%    |
| Reset 3.2 → 4.8 µm      | −5.4%    | +3.6%    | +0.3%     |

- PMOS Latch 크기 증가에서 Delay·Energy 개선 효과가 가장 크게 관측됨.
- Tail NMOS는 Noise·Energy와 Delay 사이에 뚜렷한 Trade-off 존재.
- NMOS Latch를 과도하게 축소하면 Noise·Delay·Energy 모두 악화.
- 모든 Sizing 조건에서 명목 판정 중심은 15.4 µV 이내로 측정됨.

Fig. 2. Normalized Sizing Sensitivity

- (a) Input-referred Noise
- (b) Average Delay
- (c) Energy per Comparison
- 5개 소자 그룹의 Width별 실측 결과를 Baseline = 1로 정규화한 그래프.

### B. Sensitivity-Guided Candidate Design

문단 1 — Candidate 선정

- 개별 분석에서 PMOS Latch와 Input Pair의 Width 증가가 유리한 것으로 확인.
- Candidate는 Input Pair 6.4 → 8.0 µm, PMOS Latch 1.6 → 4.8 µm로 변경.
- 나머지 소자는 Baseline 유지.
- 개별 Sizing 개선율의 합산이 아닌 조합 회로의 실제 재시뮬레이션으로 성능 검증.

문단 2 — Candidate Pre-Layout 결과 [실측]

| 항목               | Baseline | Candidate | 변화      |
| ---------------- | -------- | --------- | ------- |
| μ (µV)           | 13.061   | 12.190    | 목표 만족   |
| Noise σ (µV RMS) | 206.440  | 201.476   | −2.40%  |
| 평균 Delay (ns)    | 2.13656  | 1.47185   | −31.11% |
| Energy (pJ)      | 28.6464  | 14.2020   | −50.42% |

- Noise·Nominal Decision Center 목표 유지.
- 평균 Delay와 Energy가 동시에 크게 감소.
- Candidate의 최대 관측 Delay 약 2.17 ns.
- 확인한 시뮬레이션에서 Timeout 및 Invalid 0회.

문단 결론

- 개별 Sizing 분석 결과를 기반으로 선정한 조합에서 실제 성능 개선을 확인함.
- 해당 Candidate를 Post-Layout 검증 대상으로 선정함.

### C. Post-Layout Verification

문단 1 — Layout 및 PEX

- Baseline과 Candidate StrongARM Core의 Layout 및 PEX 수행.
- SR Latch는 두 경우 모두 동일한 Schematic 사용.
- 동일한 평가 조건에서 Noise·Delay·Energy 비교.
- 두 Core의 Layout Area 비교.

문단 2 — Post-Layout 성능 [일부 실측, 나머지 측정 예정]

Table I. Pre- and Post-Layout Performance Comparison

| Metric          | Baseline Post | Candidate Post |
| --------------- | ------------- | -------------- |
| μ (µV)          | 177.292 [실측]  | [측정 예정]        |
| σ (µV RMS)      | 123.262 [실측]  | [측정 예정]        |
| Avg. Delay (ns) | [확정 필요]       | [측정 예정]        |
| Energy (pJ)     | [확정 필요]       | [측정 예정]        |
| Core Area       | [확정 필요]       | [측정 예정]        |

실제 논문에서는 III-B의 Pre-Layout 결과와 이 Post-Layout 결과를 하나의 표로 통합하는 것을 권장.

문단 3 — 구현 후 성능 분석

- [측정 예정] Candidate의 Delay·Energy 개선이 PEX 이후에도 유지되는지 확인.
- [측정 예정] Pre/Post-Layout의 개선율 차이 분석.
- [측정 예정] Noise·Offset 목표 및 5 ns Timing 조건 확인.
- [측정 예정] 성능 개선에 따른 Layout Area 변화 평가.

Fig. 3. Baseline and Candidate Layouts

- (a) Baseline StrongARM Core.
- (b) Candidate StrongARM Core.
- 동일 확대 비율로 두 Layout과 면적 비교.

## IV. Conclusion

- StrongARM의 5개 소자 그룹에 대한 Noise·Delay·Energy 민감도를 분석함.
- PMOS Latch 크기 증가 시 평균 Delay 27.4%, Energy 49.2% 감소 확인.
- 분석 결과를 활용한 Candidate에서 Noise 2.40%, Delay 31.11%, Energy 50.42% 감소 확인.
- [측정 예정] Post-Layout 비교를 통해 개선 효과의 유지 여부와 구현 면적 비용을 검증.
- 소자 그룹별 민감도를 고려한 Sizing과 PEX 검증의 필요성을 제시.

## References

- [1] B. Razavi, “The StrongARM Latch,” IEEE Solid-State Circuits Magazine, 2015.
- [2] B. Razavi, “The Design of a Comparator,” IEEE Solid-State Circuits Magazine, 2020.
- [3] P. Nuzzo et al., “Noise Analysis of Regenerative Comparators for Reconfigurable ADC Architectures,” IEEE TCAS-I, 2008.
- [4] D. Verma et al., “A Design of Low-Power 10-bit 1-MS/s Asynchronous SAR ADC for DSRC Application,” Electronics, 2020.

## 최종 2페이지 배치 요약
![alt text](image-1.png)

최종 방향: 2페이지 논문에서는 \*\*개별 Sizing 분석(Fig. 2) → 조합 Candidate 성능 개선(Table I) → Layout 검증(Fig. 3)\*\*을 중심에 두면 돼. 나머지는 이 흐름을 설명하는 데 필요한 최소한의 내용만 작성하는 구성이야.