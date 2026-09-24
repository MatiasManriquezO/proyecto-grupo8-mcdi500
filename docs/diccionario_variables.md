# Diccionario de variables — YRBS 2023

Pool completo de preguntas del *2023 National Youth Risk Behavior Survey* (CDC).

Extraído del codebook oficial: *2023 YRBS Data User's Guide* (septiembre 2024), págs. 21–55.

> **Nota sobre la numeración:** el cuestionario impreso numera sus preguntas de corrido (1–107),
> pero las **variables del dataset** (`q1`…`q107`) siguen la numeración del codebook, que es la
> que vale. Este documento usa la del codebook.

---

## Variables usadas en este proyecto

| Variable | Rol | Pregunta | Escala |
|---|---|---|---|
| `q1` | **Covariable** | How old are you? | 7 niveles |
| `q2` | **Covariable** | What is your sex? | 2 niveles |
| `q76` | **Control** | During the past 7 days, on how many days were you physically active for a total of at least 60  | 8 niveles |
| `q80` | **EXPOSICIÓN** | How often do you use social media? | 8 niveles |
| `q84` | **DESENLACE** | During the past 30 days, how often was your mental health not good? | 5 niveles |
| `q85` | **Control** | On an average school night, how many hours of sleep do you get? | 7 niveles |

### Codificación detallada

#### `q1` — How old are you  ·  _Covariable_

> How old are you?

| Código | Respuesta |
|---|---|
| 1 | 12 years old or younger |
| 2 | 13 years old |
| 3 | 14 years old |
| 4 | 15 years old |
| 5 | 16 years old |
| 6 | 17 years old |
| 7 | 18 years old or older |

#### `q2` — What is your sex  ·  _Covariable_

> What is your sex?

| Código | Respuesta |
|---|---|
| 1 | Female |
| 2 | Male |

#### `q76` — Physical activity >= 5 days  ·  _Control_

> During the past 7 days, on how many days were you physically active for a total of at least 60 minutes per day? (Add up all the time you spent in any kind of physical activity that increased your heart rate and made you breathe hard some of the time.)

| Código | Respuesta |
|---|---|
| 1 | 0 days |
| 2 | 1 day |
| 3 | 2 days |
| 4 | 3 days |
| 5 | 4 days |
| 6 | 5 days |
| 7 | 6 days |
| 8 | 7 days |

#### `q80` — Social media  ·  _EXPOSICIÓN_

> How often do you use social media?

| Código | Respuesta |
|---|---|
| 1 | I do not use social media |
| 2 | A few times a month |
| 3 | About once a week |
| 4 | A few times a week |
| 5 | About once a day |
| 6 | Several times a day |
| 7 | About once an hour |
| 8 | More than once an hour |

#### `q84` — Current mental health  ·  _DESENLACE_

> During the past 30 days, how often was your mental health not good? (Poor mental health includes stress, anxiety, and depression.)

| Código | Respuesta |
|---|---|
| 1 | Never |
| 2 | Rarely |
| 3 | Sometimes |
| 4 | Most of the time |
| 5 | Always |

#### `q85` — Sleep  ·  _Control_

> On an average school night, how many hours of sleep do you get?

| Código | Respuesta |
|---|---|
| 1 | 4 or less hours |
| 2 | 5 hours |
| 3 | 6 hours |
| 4 | 7 hours |
| 5 | 8 hours |
| 6 | 9 hours |
| 7 | 10 or more hours |

---

## Pool completo — 86 preguntas del cuestionario

| Variable | Etiqueta | Pregunta | Niveles |
|---|---|---|---|
| `q1` ⭐ | How old are you | How old are you? | 7 |
| `q2` ⭐ | What is your sex | What is your sex? | 2 |
| `q3` | In what grade are you | In what grade are you? | 5 |
| `q4` | Are you Hispanic/Latino | Are you Hispanic or Latino? | 2 |
| `q5` | What is your race | What is your race? | 5 |
| `q6` | How tall are you | How tall are you without your shoes on? | — |
| `q7` | How much do you weigh | How much do you weigh without your shoes on? | — |
| `q8` | Seat belt use | How often do you wear a seat belt when riding in a car driven by someone else? | 5 |
| `q9` | Riding with a drinking driver | During the past 30 days, how many times did you ride in a car or other vehicle driven by | 5 |
| `q10` | Drinking and driving | During the past 30 days, how many times did you drive a car or other vehicle when you ha | 9 |
| `q11` | Texting and driving | During the past 30 days, on how many days did you text or e-mail while driving a car or  | 9 |
| `q12` | Weapon carrying at school | During the past 30 days, on how many days did you carry a weapon such as a gun, knife, o | 5 |
| `q13` | Gun carrying | During the past 12 months, on how many days did you carry a gun? | 5 |
| `q14` | Safety concerns at school | During the past 30 days, on how many days did you not go to school because you felt you  | 5 |
| `q15` | Threatened at school | During the past 12 months, how many times has someone threatened or injured you with a w | 8 |
| `q16` | Physical fighting | During the past 12 months, how many times were you in a physical fight? | 8 |
| `q17` | Physical fighting at school | During the past 12 months, how many times were you in a physical fight on school propert | 8 |
| `q18` | Saw physical violence in neighborhood | Have you ever seen someone get physically attacked, beaten, stabbed, or shot in your nei | 2 |
| `q19` | Forced sexual intercourse | Have you ever been physically forced to have sexual intercourse when you did not want to | 2 |
| `q20` | Sexual violence | During the past 12 months, how many times did anyone force you to do sexual things that  | 5 |
| `q21` | Sexual dating violence | During the past 12 months, how many times did someone you were dating or going out with  | 9 |
| `q22` | Physical dating violence | During the past 12 months, how many times did someone you were dating or going out with  | 9 |
| `q23` | Treated badly because of race or ethnicity | During your life, how often have you felt that you were treated badly or unfairly in sch | 5 |
| `q24` | Bullying at school | During the past 12 months, have you ever been bullied on school property? | 2 |
| `q25` | Electronic bullying | During the past 12 months, have you ever been electronically bullied? | 2 |
| `q26` | Sad or hopeless | During the past 12 months, did you ever feel so sad or hopeless almost every day for two | 2 |
| `q27` | Considered suicide | During the past 12 months, did you ever seriously consider attempting suicide? | 2 |
| `q28` | Made a suicide plan | During the past 12 months, did you make a plan about how you would attempt suicide? | 2 |
| `q29` | Attempted suicide | During the past 12 months, how many times did you actually attempt suicide? | 5 |
| `q30` | Injurious suicide attempt | If you attempted suicide during the past 12 months, did any attempt result in an injury, | 3 |
| `q31` | Ever cigarette use | Have you ever smoked a cigarette, even one or two puffs? | 2 |
| `q32` | Initiation of cigarette smoking | How old were you when you first smoked a cigarette, even one or two puffs? | 9 |
| `q33` | Current cigarette use | During the past 30 days, on how many days did you smoke cigarettes? | 7 |
| `q34` | Smoked > 10 cigarettes | During the past 30 days, on the days you smoked, how many cigarettes did you smoke per d | 9 |
| `q35` | Electronic vapor product use | Have you ever used an electronic vapor product? | 2 |
| `q36` | Current electronic vapor use | During the past 30 days, on how many days did you use an electronic vapor product? | 7 |
| `q37` | EVP from store | During the past 30 days, how did you usually get your electronic vapor products? | 9 |
| `q38` | Current smokeless tobacco use | During the past 30 days, on how many days did you use chewing tobacco, snuff, dip, snus, | 7 |
| `q39` | Current cigar use | During the past 30 days, on how many days did you smoke cigars, cigarillos, or little ci | 7 |
| `q40` | All tobacco product cessation | During the past 12 months, did you ever try to quit using all tobacco products? | 6 |
| `q41` | Initiation of alcohol use | How old were you when you had your first drink of alcohol other than a few sips? | 9 |
| `q42` | Current alcohol use | During the past 30 days, on how many days did you have at least one drink of alcohol? | 7 |
| `q43` | Current binge drinking | During the past 30 days, on how many days did you have 4 or more drinks of alcohol in a  | 7 |
| `q44` | Largest number of drinks | During the past 30 days, what is the largest number of alcoholic drinks you had in a row | 9 |
| `q45` | Source of alcohol | During the past 30 days, how did you usually get the alcohol you drank? | 9 |
| `q46` | Ever marijuana use | During your life, how many times have you used marijuana? | 7 |
| `q47` | Initiation of marijuana use | How old were you when you tried marijuana for the first time? | 9 |
| `q48` | Current marijuana use | During the past 30 days, how many times did you use marijuana? | 6 |
| `q49` | Ever prescription pain medicine use | During your life, how many times have you taken prescription pain medicine without a doc | 6 |
| `q50` | Ever cocaine use | During your life, how many times have you used any form of cocaine, including powder, cr | 6 |
| `q51` | Ever inhalant use | During your life, how many times have you sniffed glue, breathed the contents of aerosol | 6 |
| `q52` | Ever heroin use | During your life, how many times have you used heroin | 6 |
| `q53` | Ever methamphetamine use | During your life, how many times have you used methamphetamines | 6 |
| `q54` | Ever ecstasy use | During your life, how many times have you used ecstasy | 6 |
| `q55` | Illegal injected drug use | During your life, how many times have you used a needle to inject any illegal drug into  | 3 |
| `q56` | Ever sexual intercourse | Have you ever had sexual intercourse? | 2 |
| `q57` | Sex before 13 years | How old were you when you had sexual intercourse for the first time? | 9 |
| `q58` | Number of sex partners | During your life, with how many people have you had sexual intercourse? | 9 |
| `q59` | Current sexual activity | During the past 3 months, with how many people did you have sexual intercourse? | 9 |
| `q60` | Alcohol/drugs and sex | Did you drink alcohol or use drugs before you had sexual intercourse the last time? | 6 |
| `q61` | Condom use | The last time you had sexual intercourse, did you or your partner use a condom? | 6 |
| `q62` | Birth control pill use | The last time you had sexual intercourse with an opposite-sex partner, what one method d | 9 |
| `q63` | Sex of sexual contacts | During your life, with whom have you had sexual contact? | 8 |
| `q64` | Sexual identity | Which of the following best describes you? | 9 |
| `q65` | Transgender | Some people describe themselves as transgender when their sex at birth does not match th | 8 |
| `q66` | Perception of weight | How do you describe your weight? | 5 |
| `q67` | Weight loss | Which of the following are you trying to do about your weight? | 8 |
| `q68` | Fruit juice drinking | During the past 7 days, how many times did you drink 100% fruit juices such as orange ju | 9 |
| `q69` | Fruit eating | During the past 7 days, how many times did you eat fruit? | 9 |
| `q70` | Green salad eating | During the past 7 days, how many times did you eat green salad? | 9 |
| `q71` | Potato eating | During the past 7 days, how many times did you eat potatoes? | 9 |
| `q72` | Carrot eating | During the past 7 days, how many times did you eat carrots? | 9 |
| `q73` | Other vegetable eating | During the past 7 days, how many times did you eat other vegetables? | 9 |
| `q74` | No soda drinking | During the past 7 days, how many times did you drink a can, bottle, or glass of soda or  | 9 |
| `q75` | Breakfast eating | During the past 7 days, on how many days did you eat breakfast? | 8 |
| `q76` ⭐ | Physical activity >= 5 days | During the past 7 days, on how many days were you physically active for a total of at le | 8 |
| `q77` | PE attendance | In an average week when you are in school, on how many days do you go to physical educat | 6 |
| `q78` | Sports team participation | During the past 12 months, on how many sports teams did you play? | 4 |
| `q79` | Concussion | During the past 12 months, how many times did you have a concussion from playing a sport | 5 |
| `q80` ⭐ | Social media | How often do you use social media? | 8 |
| `q81` | HIV testing | Have you ever been tested for HIV, the virus that causes AIDS? | 3 |
| `q82` | STD testing | During the past 12 months, have you been tested for a sexually transmitted disease | 3 |
| `q83` | Oral health care | When was the last time you saw a dentist for a check-up, exam, teeth cleaning, or other  | 5 |
| `q84` ⭐ | Current mental health | During the past 30 days, how often was your mental health not good? | 5 |
| `q85` ⭐ | Sleep | On an average school night, how many hours of sleep do you get? | 7 |
| `q86` | Unstable housing | During the past 30 days, where did you usually sleep? | 9 |

⭐ = variable usada en este proyecto

---

**Fuente:** Centers for Disease Control and Prevention. (2024). *2023 YRBS data user's guide*.
https://www.cdc.gov/yrbs/media/pdf/2023/2023_National_YRBS_Data_Users_Guide508.pdf