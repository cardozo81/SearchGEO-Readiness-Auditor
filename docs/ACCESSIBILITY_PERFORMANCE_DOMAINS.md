# Acessibilidade e Web Performance — domínios separados

O SearchGEO apresenta Acessibilidade, Web Performance e Search/GEO readiness como domínios distintos para evitar mistura de métricas e conclusões.

| Domínio | Finalidade | Fonte principal | Altera Score GEO? |
|---|---|---|---|
| Search/GEO readiness | descoberta, extração, entendimento, answerability e citation readiness | evidências locais, regras e IA opcional | somente pelas regras próprias do score |
| Acessibilidade automatizada | diagnóstico auxiliar de problemas detectáveis por Lighthouse | categoria `accessibility` do artifact Lighthouse | não |
| Web Performance | lab Lighthouse + dados de campo CrUX/CWV + diagnósticos técnicos | PageSpeed/Lighthouse e CrUX | não |
| Synthetic Apdex | experiência sintética de uma Task explícita de navegação | Chromium local e perfis controlados | não |

## Acessibilidade

O relatório de Acessibilidade não é certificação WCAG. Ele apresenta somente checks automatizados e evidências efetivamente disponíveis.

A coleta não faz uma chamada externa separada: reutiliza o artifact Lighthouse obtido por PageSpeed. Assim:

```text
PageSpeed timeout/erro
→ artifact Lighthouse ausente
→ Acessibilidade automatizada não obtida
```

O report deve mostrar essa relação e a causa concreta.

## Web Performance

Web Performance pode conter:

- Lighthouse Performance;
- FCP, LCP, TBT, CLS e Speed Index de laboratório quando fornecidos;
- LCP/INP/CLS p75 de campo via CrUX quando disponíveis;
- assessment de Core Web Vitals;
- diagnóstico de recursos/bloqueios/primeira dobra conforme evidência disponível.

Dados lab e field não são intercambiáveis.

## Coleta parcial

É possível que PageSpeed falhe e CrUX direto funcione. Nesse caso, dados de campo permanecem utilizáveis, mas Lighthouse/Acessibilidade ficam indisponíveis. O estado deve ser `PARTIAL`/limitado, não sucesso integral.

## Synthetic Apdex

Apdex possui página própria e não deve ser inferido de Lighthouse/Core Web Vitals. A duração da requisição PageSpeed também não é uma amostra Apdex.

## Rastreabilidade

A página inicial do report inclui **Configuração × resultado obtido** para indicar o que foi solicitado, o que foi materializado e o motivo de qualquer ausência.
