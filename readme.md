## Social-Network Assisted Stable Task Assignment for Collective Computing

- This project is a realization of Social-Network Assisted Stable Task Assignment for Collective Computing.
- The main idea of this method is based on influence maximization and stable matching.

### Estimation of influence of worker set

For every task, the choice function runs an online algorithm with approximate ratio $\alpha$

We conbine the method of OPIM-C and budgeted influence maximization, and derive the following result:

#### sampling method I:

The first sampling method generate RR set for every task $j$ independently.

The generation of RR set follows the steps below:

1. select any node $v$ by probability $q_j(v)/Q_j$
2. generate hyperedge of all rr nodes for $v$
3. repeat step 1 and 2 until the size of RR set meets $\theta^j$

Define $\hat{f}(S;R^j)= \frac{Q_j}{\theta^j} \sum_{i=1}^{\theta^j}\mathbb{I}(S\cap R^j)$ the estimation of influence, $f(S)$ the true influence.

Denote $\theta^j$ the size of generated RR set $R^j$, define

$$
\theta_{max}^j=\frac{2Q_j}{\varepsilon^2\cdot OPT_j^k}\left(\frac{1}{4}\sqrt{\log(\frac{2}{\delta})}+\sqrt{\frac{1}{4}\log\tbinom{n_R}{k}+\log(\frac{2}{\delta})}\right)^2
$$

If $\theta^j\geq \theta_{max}^j$ and $S^*$ is the outcome of an algorihtm of which approximate rate is $1/4$ using $\hat{f}(S;R^j)$ as the estimation of influence, then $Pr[f(S^*)\geq(\frac{1}{4}-\varepsilon)OPT_j]\geq 1-\delta $

The sampling alogrithm follows the steps below:

1. set $\theta^j = \theta^j_0$, $i_{max}=\log_2(\theta^j_{max}/\theta^j_0)$
2. generate RR set R1 and R2, and compute $f^l(S^*), f^u(S^o)$
3. if $f^l(S^*)/f^u(S^o)\geq \frac{1}{4}-\varepsilon $ or $i\geq i_{max}$, go to step 4;
   else double the size of R1, R2 and $i\gets i+1$, go to step 2
4. return R1

Using R1 and R2, we calculate $f^l(S^*), f^u(S^o)$ ：

$$
f^l(S^*) = \frac{Q_j}{\theta}\left[\left(\sqrt{\frac{\theta}{Q_j}\hat{f}(S^*;R_2)+\frac{2\log(1/\delta_2)}{9}}-\sqrt{\frac{\log(1/\delta_2)}{2}}\right)^2-\frac{\log(1/\delta_2)}{18}\right]
$$

$$
f^u(S^o)= \frac{Q_j}{\theta}\left(\sqrt{\frac{\theta}{Q_j}\hat{f}(S^o;R_1)+\frac{\log(1/\delta_1)}{2}}+\sqrt{\frac{log(1/\delta_1)}{2}}\right)^2
$$

By $\hat{f}(S^o;R_1)\leq 4 \hat{f}(S^*;R_1)$



