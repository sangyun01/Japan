# ICEIC 2027 Draft (English) — StrongARM Latch Comparator Sizing Sensitivity (2 pages)

> **표기 규칙**
> - **[TBD: …]** — 채울 값 (PDF·Word에서 노란색)
> - **[CHECK: …]** — 붙여주신 원문이나 측정값에 없어 제가 넣었거나, 그래프 판독값처럼 확인이 필요한 문장·수치 (PDF에서 파란색, Word에서 청록색)
>
> 조판본: [ICEIC2027_draft_en.pdf](ICEIC2027_draft_en.pdf) — 1~2쪽 원고, 3쪽 검토 메모
> Word: [ICEIC2027_draft_en.doc](ICEIC2027_draft_en.doc) — 양식 .doc을 바탕으로 만든 제출용 원고 (검토 메모 제외)
> 한국어판: [ICEIC2027_draft_ko.md](ICEIC2027_draft_ko.md) · [.pdf](ICEIC2027_draft_ko.pdf) · [.doc](ICEIC2027_draft_ko.doc)

---

## Part 1. 검토 메모 (영문판)

### 1. 한국어판과의 관계

내용은 한국어판(ICEIC2027_draft_ko)과 같습니다. 문장 단위로 옮기되 영어 논문 관례에 맞게 다듬었습니다. 빈칸(노란색)과 확인할 문장(파란색)도 한국어판과 같은 자리에 있습니다. 각 항목의 근거와 판정 시점·지연 문제는 한국어판 검토 메모 2절과 5절을 보세요.

### 2. 영문판에서 새로 정한 것

| 항목 | 영문판 | 확인할 점 |
|---|---|---|
| 제목 | Transistor Sizing Sensitivity Analysis of a StrongARM Latch Comparator for SAR ADCs | 24pt에서 2줄에 들어가도록 "and Performance"를 뺐습니다. |
| 저자 이름 | Dongui Hong, Min Kim, Doohyung Kim, Sangyun Kim, Wooeun Choi | 제가 추정한 표기입니다(파란색). 각자 쓰는 영문 이름으로 바꿔 주세요. |
| 소속 | School of Electrical and Electronics Engineering, Chung-Ang University, Seoul, Republic of Korea | 학부의 공식 영문 명칭인지 확인해 주세요. |
| 그림·표 번호 | 양식의 자동 번호(Fig. 1., TABLE I.)를 사용 | Word에서 캡션 앞 번호는 자동으로 붙습니다. |
| 핵심어 | 한국어판과 같이 넣지 않음 | 학회가 요구하면 초록 아래에 추가합니다. |
| 사사 | 양식의 영문 문구 그대로 ("The This" 오타만 수정) | — |
| 그림 자리 안내 | 영어로 표기 | 그림을 넣을 때 상자 안 글자를 지웁니다. |

### 3. 분량

양식과 같은 치수(A4, 1단, 본문 10pt)로 조판한 결과, 원고는 Word와 PDF 모두 **2페이지 안에 들어갑니다.** 2페이지 끝에 남는 공간은 Word에서 약 3줄, 이 PDF에서 약 2줄입니다. 빈칸에 실제 결과 문장이 들어가 넘치면, 한국어판 검토 메모 3절의 순서(12 MHz 문장 삭제 → 그림 2 높이 축소 → 잡음 감소 원인 문장 삭제)대로 줄입니다.

### 4. 용어 대응

| 한국어판 | 영문판 |
|---|---|
| 판정 임계값(오프셋) | decision threshold (offset) |
| 입력 환산 잡음 | input-referred noise |
| 비교 지연 시간 / 비교당 에너지 | comparison delay / energy per comparison |
| 교차 결합 NMOS·PMOS 쌍 | cross-coupled NMOS and PMOS pairs |
| 사이징 분석 | sizing analysis |
| 클록 high 구간의 80% 시점에서 판정 | read at 80% of the clock-high phase |
| 판정 임계값 부근 | near the (decision) threshold |

---

## Part 2. 원고 초안 (English)

# Transistor Sizing Sensitivity Analysis of a StrongARM Latch Comparator for SAR ADCs

**Authors** (all *School of Electrical and Electronics Engineering*, *Chung-Ang University*, Seoul, Republic of Korea; 3 in the first row · 2 in the second) — 영문 이름 표기는 확인 필요

| Dongui Hong (홍동의) | Min Kim (김민) | Doohyung Kim (김두형) |
|:---:|:---:|:---:|
| darwin5991@cau.ac.kr | kimminjoshua@cau.ac.kr | engud5027@naver.com |

| Sangyun Kim (김상윤) | Wooeun Choi (최우은) |
|:---:|:---:|
| goodalbert@naver.com | w030901@naver.com |

---

**Abstract** — This paper presents a StrongARM latch comparator for a 10-bit successive-approximation-register (SAR) analog-to-digital converter (ADC), designed in a 500-nm CMOS process, and examines how transistor sizing affects its performance. The comparator consists of a StrongARM latch and an SR latch. With a baseline that meets the offset and noise targets as the reference, the width of each transistor group was varied to compare the resulting changes in input-referred noise, comparison delay, and energy per comparison. The StrongARM core of the baseline was laid out and verified by post-layout simulation with extracted parasitics, which yielded an offset of 177.3 µV (0.073 LSB) and an input-referred noise of 123.3 µV rms (0.050 LSB). **[TBD: One sentence summarizing the key sizing result]**

## I. Introduction

A SAR ADC converts an analog input into a digital code through a binary search performed by a single comparator [3]. The accuracy, speed, and energy of the comparator therefore directly affect those of the ADC. The StrongARM latch draws no static current and amplifies a small input difference to digital levels through positive feedback, which makes it well suited to SAR ADCs [1], [2]. Its performance, however, depends strongly on transistor sizing. Enlarging a device can improve one metric, but it also increases parasitic capacitance and energy consumption and may degrade other metrics. Even after the targets are met, it is therefore worth knowing how much extra energy a further improvement costs and which devices can be made smaller. In this work, a baseline StrongARM comparator for a 10-bit SAR ADC is designed and verified through layout, and its noise, delay, and energy are compared as the width of each transistor group is varied.

## II. Circuit Design and Specifications

The target application is a 10-bit, 1-MS/s SAR ADC. With a differential full-scale range of 2.5 V, 1 LSB is 2.441 mV, so the targets were set to an offset below 0.5 LSB (1.221 mV) and an input-referred noise below 0.1 LSB (244 µV rms). The supply voltage is 5 V, and the input common-mode voltage is 2.5 V. The comparator was characterized with an 80-MHz clock, and the SR-latch output was read at 80% of the clock-high phase. **[CHECK: This is stricter than the 12-MHz clock needed for 1-MS/s operation when the 1-µs conversion period is divided into 12 clock cycles.]**

Fig. 1(a) shows the schematic of the designed comparator. It consists of an input differential pair, a tail transistor, cross-coupled NMOS and PMOS pairs, reset transistors at the output nodes (P/Q) and the internal nodes (X/Y), and an SR latch that holds the decision. The baseline was sized to meet the offset and noise targets while ensuring proper reset and regeneration. The widths are 6.4 µm for the input pair, 1.6 µm (the process minimum) for the cross-coupled PMOS pair, and 3.2 µm for all other groups, and all devices share a channel length of **[TBD]** µm. Symmetric devices are sized identically.

> **[그림 자리 · 높이 32 mm]** Fig. 1(a) placeholder: StrongARM + SR latch schematic | Fig. 1(b) placeholder: StrongARM core layout
>
> Fig. 1. (a) Schematic of the designed comparator (widths in µm, *L* = **[TBD]** µm) and (b) layout of the StrongARM core (**[TBD]** µm × **[TBD]** µm).

## III. Simulation Results and Discussion

### A. Transistor Sizing Sensitivity

The width of one group at a time was scaled to 0.5× and 2× of its baseline value while the other groups were kept at the baseline. Because the cross-coupled PMOS pair is already at the minimum width, only the 2× case was applied to it. The sizing analysis was carried out at the schematic level. The input-referred noise was obtained from transient noise simulations: at each differential input *V*<sub>diff</sub>, the probability of a high decision was measured over **[TBD: N]** comparisons and fitted to a Gaussian cumulative distribution function (CDF) [4],

$$
P(\mathrm{High}) = \Phi\!\left(\frac{V_{\mathrm{diff}}-\mu}{\sigma}\right) \tag{1}
$$

where *μ* is the decision threshold (offset) and *σ* is the rms input-referred noise. The comparison delay was defined as **[CHECK: the time from the rising clock edge until the SR-latch output crosses *V*<sub>DD</sub>/2]**, and the energy per comparison as the energy drawn from the supply over one clock period, including the reset and evaluation phases. Delay and energy were compared at *V*<sub>diff</sub> = **[CHECK: ±1.221 mV (0.5 LSB)]**.

Fig. 2 shows the noise, delay, and energy of each case relative to the baseline. **[TBD: Result 1: the group with the largest effect, with numbers]** **[TBD: Result 2: a group whose upsizing costs more energy than it gains]** **[TBD: Result 3: a group that can be downsized to save energy]**

> **[그림 자리 · 높이 24 mm]** Fig. 2(a): input-referred noise change (%) | Fig. 2(b): comparison delay change (%) | Fig. 2(c): energy per comparison change (%)
>
> Fig. 2. Change in (a) input-referred noise, (b) comparison delay, and (c) energy per comparison when the width of each transistor group is scaled to 0.5× and 2×.

### B. Post-Layout Verification of the Baseline

Parasitic resistance, capacitance, and coupling capacitance were extracted from the layout in Fig. 1(b) for post-layout simulation, while the SR latch was kept at the schematic level. Sweeping *V*<sub>diff</sub> from −1.2 mV to +1.2 mV in 60 steps gave the CDF in Fig. 3, from which *μ* = 177.3 µV and *σ* = 123.3 µV rms were extracted. These correspond to 0.073 LSB and 0.050 LSB and satisfy both targets. As listed in Table I, the decision threshold shifted from 8.4 µV before layout to 177.3 µV; this systematic offset can be attributed to asymmetric layout parasitics. The random offset due to device mismatch was not included in this analysis. The noise, on the other hand, decreased from 142.6 µV to 123.3 µV rms, **[CHECK: presumably because the extracted capacitance lengthened the integration time at nodes X and Y]**.

Both the delay and the energy peaked near the decision threshold, where the regeneration of the latch slows down. The average delay was **[CHECK: about 4.5 ns]** at |*V*<sub>diff</sub>| = 1.2 mV and **[CHECK: about 5.7 ns (maximum about 6.2 ns)]** near the threshold, well below the **[CHECK: approximately 33 ns]** allowed at 1 MS/s.

> **[그림 3 자리 (왼쪽, 86 × 33 mm) | 표 1 (오른쪽)]**
>
> Fig. 3. Post-layout probability of a high decision versus *V*<sub>diff</sub> and the fitted Gaussian CDF.

**TABLE I. Pre- and Post-Layout Performance of the Baseline**

| Metric | Pre-layout | Post-layout |
|---|:---:|:---:|
| Decision threshold *μ* (µV) | 8.4 | 177.3 |
| Input-referred noise *σ* (µV rms) | 142.6 | 123.3 |
| Comparison delay (ns)<sup>a</sup> | **[TBD]** | **[CHECK: 4.5–5.7]** |
| Energy per comparison (pJ)<sup>a</sup> | **[TBD]** | **[CHECK: 37–77]** |

<sup>a</sup> Average values at |*V*<sub>diff</sub>| = 1.2 mV and near the decision threshold.

## IV. Conclusion

A StrongARM comparator for a 10-bit SAR ADC was designed, and the effect of transistor sizing on its performance was analyzed. After layout, the baseline achieved an offset of 177.3 µV and an input-referred noise of 123.3 µV rms, meeting the targets. In the sizing analysis, **[TBD]** had the largest effect on noise and **[TBD]** on delay, while **[TBD]** could be downsized to save energy with little performance loss. Although the sizing results come from schematic-level simulations, they can serve as a reference when choosing device sizes under combined accuracy and energy constraints.

## Acknowledgment

This paper was supported by Korea Institute for Advancement of Technology (KIAT) grant funded by the Korea Government (Ministry of Education) (P0030093, “Semiconductor”-Specialized University).

## References

[1] B. Razavi, “The StrongARM latch [A circuit for all seasons],” *IEEE Solid-State Circuits Mag.*, vol. 7, no. 2, pp. 12–17, Spring 2015.

[2] B. Razavi, “The design of a comparator [The analog mind],” *IEEE Solid-State Circuits Mag.*, vol. 12, no. 4, pp. 8–14, Fall 2020.

[3] C.-C. Liu, S.-J. Chang, G.-Y. Huang, and Y.-Z. Lin, “A 10-bit 50-MS/s SAR ADC with a monotonic capacitor switching procedure,” *IEEE J. Solid-State Circuits*, vol. 45, no. 4, pp. 731–740, Apr. 2010.

[4] P. Nuzzo, F. De Bernardinis, P. Terreni, and G. Van der Plas, “Noise analysis of regenerative comparators for reconfigurable ADC architectures,” *IEEE Trans. Circuits Syst. I, Reg. Papers*, vol. 55, no. 6, pp. 1441–1454, Jul. 2008.
