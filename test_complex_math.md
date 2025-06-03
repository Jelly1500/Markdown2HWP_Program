# 첨단 교통 시스템(ITS) 도입에 따른 기대효과 분석 모델 연구 (요약)

## 1. 서론
본 연구는 첨단 교통 시스템(ITS) 도입 시 예상되는 사회경제적 편익을 계량적으로 분석하기 위한 복합 모델을 제시한다. 모델은 주로 통행시간 단축 효과 $T_s$ 와 교통사고 감소 효과 $A_r$ 을 중심으로 구성된다.

## 2. 모델의 기본 구조

### 2.1. 통행시간 단축 편익 ($B_{TS}$)
통행시간 단축 편익은 다음 적분 형태로 정의된다:
$$
B_{TS} = \int_{t_0}^{t_f} \left( V(t)_{before} - V(t)_{after} \right) \cdot N(t) \cdot C_{time} dt
$$
여기서,
- $V(t)_{before}$: ITS 도입 전 시간 $t$에서의 평균 통행시간
- $V(t)_{after}$: ITS 도입 후 시간 $t$에서의 평균 통행시간
- $N(t)$: 시간 $t$에서의 교통량
- $C_{time}$: 시간 가치 비용 (단위: 원/시간)

### 2.2. 교통사고 감소 편익 ($B_{AR}$)
교통사고 감소 편익은 사고 유형별 감소율과 사회적 비용을 고려하여 산출한다. 사고 유형 $k$에 대한 연간 사고 감소 건수를 $\Delta A_k$, 유형별 평균 사회적 비용을 $C_k$라 할 때, 총 편익은 다음과 같다.
$$
B_{AR} = \sum_{k=1}^{K} (\Delta A_k \cdot C_k)
$$
여기서 $\Delta A_k$는 다음 행렬식의 일부로 도출될 수 있는 예측 모델 $f(\mathbf{X})$의 결과에 의존한다.
$$
\mathbf{Y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}
\quad \text{where} \quad
\mathbf{X} = \begin{pmatrix}
X_{11} & \cdots & X_{1p} \\
\vdots & \ddots & \vdots \\
X_{n1} & \cdots & X_{np}
\end{pmatrix},
\boldsymbol{\beta} = \begin{pmatrix} \beta_1 \\ \vdots \\ \beta_p \end{pmatrix}
$$

## 3. 확률적 시뮬레이션 모델

미래 예측의 불확실성을 반영하기 위해 몬테카를로 시뮬레이션을 활용한다. 특정 변수 $x$가 다음 확률분포 $P(x)$를 따른다고 가정한다.
$$
P(x) = \frac{1}{\sqrt{2\pi\sigma^2}} e^{ - \frac{(x-\mu)^2}{2\sigma^2} }
$$
또한, 조건부 확률 $P(A|B) = \frac{P(A \cap B)}{P(B)}$ 개념을 적용하여 시나리오별 가중치를 부여한다.

## 4. 다중 기준 의사결정 모델 (AHP 활용)

정책 대안 $A_i$의 우선순위 $w_i$를 결정하기 위해 계층 분석적 의사결정 과정(AHP)을 일부 활용하며, 쌍대비교 행렬 $\mathbf{M}$은 다음과 같다.
$$
\mathbf{M} = \begin{pmatrix}
1 & w_1/w_2 & \cdots & w_1/w_n \\
w_2/w_1 & 1 & \cdots & w_2/w_n \\
\vdots & \vdots & \ddots & \vdots \\
w_n/w_1 & w_n/w_2 & \cdots & 1
\end{pmatrix}
$$
이 행렬의 최대 고유값 $\lambda_{max}$ 와 고유벡터를 활용하여 일관성 지수(CI) $CI = \frac{\lambda_{max}-n}{n-1}$ 를 계산한다.

## 5. 조건부 기대값 함수 예시

특정 조건 하에서의 기대값 함수 $E[X|Y=y]$는 다음과 같이 표현될 수 있다.
$$
E[X|Y=y] = \begin{cases}
\int_{-\infty}^{\infty} x f_{X|Y}(x|y) dx & \text{ (연속 확률 변수)} \\
\sum_{x} x P_{X|Y}(x|y) & \text{ (이산 확률 변수)}
\end{cases}
$$
여기서 $f_{X|Y}(x|y)$는 조건부 확률 밀도 함수, $P_{X|Y}(x|y)$는 조건부 확률 질량 함수이다. 