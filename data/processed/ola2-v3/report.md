# Ola2 Structure Explorer Report

## Run Header
- run_id: dcf956fc-f99c-40ed-bd1f-8606aa76d326
- started_utc: 2025-12-22T07:50:13Z
- finished_utc: 2025-12-22T10:10:14Z
- duration_seconds: 8400.44
- code_version: sha256:0a0b82eaf6ecafd69622c0a01f0ab36fa8604d8e197189f6e0895ba65548bf70
- attempts_path: data/processed/ola2-v3/attempts.jsonl
- attempts_size_mb: 861.41
- species_catalog_path: data/processed/ola2-v3/species_catalog.jsonl
- species_catalog_size_mb: 121.95
- report_path: data/processed/ola2-v3/report.md
- report_size_mb: 0.03
- config_path: data/raw/structure_explorer_v3.json
- config_sha256: sha256:7295f09eb3317c970e58cb976de72079b2dec32715434ece861328c8d120141b
- templates_path: data/raw/compound_templates_v3.json
- templates_sha256: sha256:8c9e5151e4807faf8466e8486d2ae3fea1af16ef8ac3e85bec433f2d996b07e4
- inputs.blocks_mode: ola1_blocks
- inputs.blocks_json: data/processed/ola1/simple_blocks.json
- observer.hbar_sim_used: 0.3197070890315956
- observer.mass_est_units: GeV per rad/time_unit
- observer.mass_est_method: mass_est = hbar_sim_used * omega_eff

## Targets Used
| target_name | templates | allowed_block_families | budget_evals |
| --- | --- | --- | --- |
| atomic_search_all | ['alpha_tetrahedron', 'atomic_nucleus_heavy'] | [] | 200000 |

## Templates Used
| template_name | nodes | edges | notes |
| --- | --- | --- | --- |
| alpha_tetrahedron | 4 | 6 | nucleus |
| atomic_nucleus_heavy | 6 | 9 | atom_core |

## Universe Summary
- total_attempts: 129710
- unique_structures: 80000
- viable_attempts: 38915 (30.00%)
- rejected_attempts: 90795 (70.00% )
- best_attempt: structure_id=7b6e97a36898f30fa5ae24767caf19fe4dec31715356d51d850094706379445d template=alpha_tetrahedron target=atomic_search_all
  R_mean_lastW=0.9989189483734027 phase_var_lastW=8.879194476624402e-05 memory_score_k10=0.9734817483680532 QualityLock=0.7497389596582432 entropy_quality=0.996615494436598 omega_eff=0.09359756242480495
- top_reasons: [('low_coherence', 90261), ('high_phase_variance', 89770), ('memory_non_positive', 42168), ('low_quality_lock', 21953)]

## DOF Mass Preview (observer-only, no SM)
- mass_index := omega_eff  (adimensional)
- mass_est := hbar_sim_used * omega_eff  (units: GeV per rad/time_unit)
- hbar_sim_used: 0.3197070890315956

### Top Species by Stability (with DOF mass)
| rank | species_id | template | n_trials | seed_stability | omega_eff (mass_index) | mass_est | R_mean_lastW | phase_var_lastW | memory_score_k10 | QualityLock | entropy_quality |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 3ff6ae9a7d1e37c82105538fc65e578da6bf732e02fba767a3cf0c4df349b7c4 | alpha_tetrahedron | 16 | 1.000 | 0.00116664494465408 | 0.0003729846591887829 | 0.9764829638734774 | 0.00032325901332320685 | 0.8464735404492778 | 0.9998399059251287 | 0.9985156015895275 |
| 2 | 6a38fdd1e85ec52048b1a1185336b1165b2d3828ba89e209e936bfac8e747ec3 | alpha_tetrahedron | 16 | 1.000 | 0.16563489954748223 | 0.0529546515763663 | 0.9959295729742562 | 0.00011866901642470784 | 0.9604895462907733 | 0.9998376466003083 | 0.9984987759563232 |
| 3 | e0c2a0c43cec1316962abd82a264c5741632eb4c190899923251d0eaa9d015a7 | alpha_tetrahedron | 16 | 1.000 | 0.0007126860578712337 | 0.0002278507849554154 | 0.9840608181454946 | 0.00012002195473718111 | 0.9641934270753085 | 0.9998365246394612 | 0.9984927229724477 |
| 4 | 027920ce3966115546c0eedcfb14af9cf84e44ee6b8517640bbb473ba0aca6a0 | alpha_tetrahedron | 16 | 1.000 | 0.00045771616108925315 | 0.00014633510146456203 | 0.9813899982383768 | 3.130543586008059e-05 | 0.9788142126872063 | 0.9998273338578906 | 0.9983976131500312 |
| 5 | 11004c2291887c1470cdc723004c170948172334f291b3b4dc14246c3fcb470c | alpha_tetrahedron | 16 | 1.000 | 0.002271503027820017 | 0.0007262156207507932 | 0.9860015803735154 | 0.0005064772404610453 | 0.9138379712339559 | 0.9998272959405463 | 0.9984011071694326 |
| 6 | d7f4096bded598d8e261d17322e3fa5bd093d6b547febcac461472774375d84b | alpha_tetrahedron | 16 | 1.000 | 0.14213713046833218 | 0.045442248225334596 | 0.9942813003154474 | 5.075229919855563e-05 | 0.9367835488040361 | 0.9998179761518586 | 0.9983509785383279 |
| 7 | bcc4ddeda7a59afd909e12ebd44efc8d2777f840ebd87b66e702d961b1497a83 | alpha_tetrahedron | 16 | 1.000 | 0.001347218273794335 | 0.000430715232604958 | 0.9857558908878972 | 0.00032353252974126265 | 0.951434152307542 | 0.9998115490435218 | 0.9982843238352236 |
| 8 | 5ff53bb82826416a9314ed1f83e0bc5f50fb6275589dcb1f3fa3dd64a260c0f5 | alpha_tetrahedron | 16 | 1.000 | 0.0005676422108119883 | 0.00018147923883016012 | 0.9769330301642318 | 4.7365712332226745e-05 | 0.9550708712485966 | 0.9998080777391167 | 0.9982489640332008 |
| 9 | e80dacdcc2354cd4e67b897e9586681f0eef5110cdd19612025eac8aa02348b2 | alpha_tetrahedron | 16 | 1.000 | 0.0028636234140463263 | 0.0009155207057874706 | 0.9886698123696027 | 0.0005307073019747752 | 0.9027303505390338 | 0.9998044948778455 | 0.9982215372712336 |
| 10 | d74d859c58e4c0fdf79a56c630b78508b59b3cb705962b06156105450cd560fc | alpha_tetrahedron | 16 | 1.000 | 0.0022019059923537926 | 0.0007039649551366579 | 0.9953822813395723 | 0.00016825388526310017 | 0.9726409048243371 | 0.999799987220592 | 0.9981867132768607 |
| 11 | 3e0f3b43756dc677e48cd2aeb4c2ec9229672fdb87c2c0d46d07fa189033ce99 | alpha_tetrahedron | 16 | 1.000 | 0.0029831932096956 | 0.0009537480170906027 | 0.9904527646964822 | 4.142815585122082e-05 | 0.9480820854265297 | 0.9997982059702819 | 0.9981773632000774 |
| 12 | 7f3f625d664b533b65eaba34f7f9baa0e91bcec1ed4f6921887dabab21998749 | atomic_nucleus_heavy | 16 | 1.000 | 0.002425091028695081 | 0.0007753187934207421 | 0.9952173664260193 | 0.0001781456735065101 | 0.9647620445955218 | 0.9997938489458572 | 0.9981483164989111 |
| 13 | ea6f2cc8aadc22f331e4c12008db9665a16a1c59d6a8b187df0184c16f7a7988 | alpha_tetrahedron | 16 | 1.000 | 0.003349701624698798 | 0.001070923355556859 | 0.9876466258671266 | 0.0003516656874588742 | 0.8985270330295921 | 0.9997909786831352 | 0.9981346597935385 |
| 14 | 81bba495a284cc0ba62b7c89956fac36a8961514468271a23c558e57a00f401c | alpha_tetrahedron | 16 | 1.000 | 0.009070489782516476 | 0.0028998998844591735 | 0.9907432416570975 | 0.0008031205549005336 | 0.9316188523552446 | 0.9997903004072611 | 0.9981347477433988 |
| 15 | 4e439ca60e6f233f6513cea8c76e260f8b04de2ad19aefe49afe5b4f40867116 | alpha_tetrahedron | 16 | 1.000 | 0.07362736290170457 | 0.023539189866376865 | 0.9901470567280312 | 0.00010518355527897411 | 0.9739045177880126 | 0.9997832372166104 | 0.998032572899722 |
| 16 | 363f805a9be9cf54c0ba1f673f158c427f8387e3f76478ef41cd2f71ad920a4a | alpha_tetrahedron | 16 | 1.000 | 0.002445065670440946 | 0.0007817048279877615 | 0.9887997548622994 | 0.0008658196281984527 | 0.8596366825851338 | 0.9997698131413525 | 0.997919043981758 |
| 17 | c5bca79677c142eceebe6f227044109f19385eb011e2eccf54b85db705616263 | alpha_tetrahedron | 16 | 1.000 | 0.0008315816656179131 | 0.0002658625536067487 | 0.9895978760148335 | 0.00014604505425810986 | 0.9147821767841419 | 0.9997630462351992 | 0.9978774769059372 |
| 18 | 6aab9dad289b546aff3965bf8f810d33cbefc59a6ccb47659f26a724aba065bd | alpha_tetrahedron | 16 | 1.000 | 0.21092190888761309 | 0.06743322950344621 | 0.9986499079665514 | 0.0008381526348007626 | 0.8824393176571897 | 0.9997619448200459 | 0.9979261242357261 |
| 19 | 77747813d014221b814ae56dfc62d58d903a717c92914614e2037a94f20bf742 | alpha_tetrahedron | 16 | 1.000 | 0.0005842123091645713 | 0.00018677681673943166 | 0.9909345987667736 | 0.00028131852947772254 | 0.9576114711297415 | 0.9997523080009124 | 0.9977904419526881 |
| 20 | ef52f772e369c598843dfcde62e629948f933de449bb7d474315422f10a09e8e | alpha_tetrahedron | 16 | 1.000 | 0.004850439794209226 | 0.0015507199871296433 | 0.9953750619492338 | 8.36068584693354e-05 | 0.9265234819394884 | 0.9997517036913952 | 0.9978417761079242 |

### DOF Mass Summary by Species (no SM)
| species_id | template | mass_est_mean | mass_est_min | mass_est_max | mass_est_std | omega_eff_mean | memory_mean | R_mean | n |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |

### Mass Bands (counts)
- [0,0.5): 115039
- [0.5,1.0): 14671
- [1.0,2.0): 0
- [2.0,4.0): 0
- [4.0,8.0): 0
- [8.0,16.0): 0
- [16.0,+): 0

mass_est es un observer scalar (hbar_sim_used) aplicado a ω_eff para orientar exploración. No interviene en búsqueda, tags ni viabilidad.

## Phase Breakdown
| phase | attempts | viable_rate | unique |
| --- | --- | --- | --- |
| phase1 | 80000 | 4.29% | 80000 |
| phase2 | 49710 | 71.38% | 3314 |

- seed_repeats_per_structure: 15
- param_neighbor_bins: 3
- promising_rule: None

## Taxonomy & Tags
### Attractor Class
| attractor_class | count | pct |
| --- | --- | --- |
| COHERENT_LOCKED | 38915 | 30.00% |
| DRIFT_BOUNDED | 90795 | 70.00% |

### Grade
| grade | count | pct |
| --- | --- | --- |
| A | 38915 | 30.00% |
| C | 90795 | 70.00% |

### Tags
| tag | count | pct |
| --- | --- | --- |
| ZOMBIE | 42168 | 32.51% |

ZOMBIE rule: memory_score_k10 <= 0

## Histograms
### R_mean_lastW
- 0-0.5: 55528
- 0.5-0.7: 25687
- 0.7-0.85: 11131
- 0.85-0.9: 3435
- 0.9-0.95: 9206
- 0.95-0.98: 13922
- 0.98-1.0: 10801
- 1.0+: 0

### phase_var_lastW
- 0-1e-6: 0
- 1e-6-1e-4: 5905
- 1e-4-1e-3: 31143
- 1e-3-1e-2: 2486
- 1e-2-1e-1: 538
- 1e-1+: 89638

### memory_score_k10
- [-inf,-10): 1228
- [-10,-1): 8536
- [-1,0): 32404
- [0,0.5): 35854
- [0.5,0.8): 22127
- [0.8,1.0): 29561
- [1.0,inf): 0

### omega_eff
- 0-0.5: 56431
- 0.5-1: 22788
- 1-2: 48076
- 2-5: 2415
- 5-10: 0
- 10-20: 0
- 20+: 0

### entropy_quality
- 0-0.2: 0
- 0.2-0.4: 0
- 0.4-0.6: 0
- 0.6-0.8: 0
- 0.8-0.9: 0
- 0.9-1.0: 129710
- 1.0+: 0

## LS View Settings
- max_den: 31
- epsilon_rel: 0.001
- attempts_with_LS: 120395
### Top LS Hashes
- 391e90fcea76f4f1d639c7f65ffeb636b938e2903c2c16059b106f7d5279c7d1: 1104
- 599b6f943458436c41b9056ae26955f5858f08f5a054de4ef42a8926854b1130: 1070
- 84f2b00b2c1814bfec00d0b739b3a872cb28ff1f7ca12bdf85b23709e3f5f36e: 1028
- d1ca667938b5ea006c654cce3dc904f20fcf1e267ecd0c3f36ed85575128de30: 1012
- f3e71eb05d7ecb91f96694eba11ec96a69aed955fd686df64822a68169404c4d: 948
- e92389de5ff60a672bd2f67545eee7e81ed2243c256051a3abc0ff1e996da75d: 942
- fb0f2ce98c7d435dc1be596d62e9b83009740508eee76e48355a6e353e153265: 345
- 120359163c88ede1aefbf0892480efd2876be834e881543f132c732b2e103619: 260
- 5ae02c680a99e49bafe667a73935825889069a636d8276bc95e389ec90bb8c6a: 255
- f91fb539509d2983c4a9f49f6a0a17c5f84c13bf6da0f8de82e736580f60e748: 236

## Template Stats
| template_name | nodes | attempts | unique | viable_rate | best_R | best_memory |
| --- | --- | --- | --- | --- | --- | --- |
| alpha_tetrahedron | 4 | 80725 | 40000 | 40.60% | 0.9989189483734027 | 0.9734817483680532 |
| atomic_nucleus_heavy | 6 | 48985 | 40000 | 12.53% | 0.99579729998916 | 0.9826754205212004 |

## Target Stats
| target_name | templates | attempts | unique | viable_rate | notes |
| --- | --- | --- | --- | --- | --- |
| atomic_search_all | ['alpha_tetrahedron', 'atomic_nucleus_heavy'] | 129710 | 80000 | 30.00% |  |

## Species Catalog (Top 20 by seed_stability)
| species_id | template | trials | seed_stability | omega_eff | memory | entropy_quality | QualityLock | zombie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3f6a095d0c7f5640a2c7aaf0b0ce001be0faa43143e7ebbdd43831930b9d83ad | alpha_tetrahedron | 16 | 1.000 | 0.12270658628414507 | 0.914037256277396 | 0.9935793353036735 | 0.9991529411161281 | 0.0 |
| 494201c40628c951eed0bf4f0cb23a93248d93c759ad9a0a7f9fd9817fe6ccc4 | alpha_tetrahedron | 16 | 1.000 | 0.0031037786157698108 | 0.968376511180063 | 0.9965052636295032 | 0.99955433730431 | 0.1875 |
| 6d2ea79077de856b9229731951054819689e253642d0cf8bec5b9dcd5c414b49 | alpha_tetrahedron | 16 | 1.000 | 0.0464133684782875 | 0.9437878163304739 | 0.994708248036853 | 0.7497272189855135 | 0.0625 |
| 4fd1f9aed7983467ed588821681d7ed63de2ba0d9e683e9529798e470e2f8726 | alpha_tetrahedron | 16 | 1.000 | 0.05553198338025521 | 0.9459369733421765 | 0.9975566889586758 | 0.9997222830375031 | 0.0625 |
| f30970c6d5f94b36e0117ad2daf2105d237cfe16024fa9973d235e77b8d0d631 | alpha_tetrahedron | 16 | 1.000 | 0.0015973920355432825 | 0.9513143504117239 | 0.9944086665706324 | 0.9992769002695412 | 0.0 |
| bceac9e2eeb9ccd1c7ae2884f6ce198af5de0b3693350d714f1d6866ed5c1c92 | alpha_tetrahedron | 16 | 1.000 | 1.5001797151457525 | 0.8629608447546234 | 0.9931723532454845 | 0.9990893798580697 | 0.0625 |
| 508a642cd35ad53445734411a3aa3a5b2fa04c644ad82b0ce68297bd8ffea4b3 | alpha_tetrahedron | 16 | 1.000 | 0.2839404225505154 | 0.9289449185826243 | 0.9940087418059002 | 0.9992329525922726 | 0.0 |
| c92e9b1ff1f22367ce0796cdc82ca334185bf125885e7f8b4e4eb856cb10f395 | alpha_tetrahedron | 16 | 1.000 | 0.0686073871516457 | 0.919932569746522 | 0.9961864897988684 | 0.9995277682321222 | 0.0 |
| 642e1b8f4381da661d23df3794df8b306ecc591ffc9c2b0d350fee0e10e0a2f6 | alpha_tetrahedron | 16 | 1.000 | 0.1361403409037897 | 0.9472985605062187 | 0.9941589601599755 | 0.9992170811164297 | 0.0 |
| 661cdadcfc5832590f909da4abedd86faac9a0b0ad33bb002f1721ef8d7a9d97 | atomic_nucleus_heavy | 16 | 1.000 | 0.0009157673318822527 | 0.9570637590618014 | 0.9973474648232435 | 0.9996863890394297 | 0.0 |
| 82df9f6241c8fa4d600cd77d742d4a689d408bfca19170c6a8b4e94a1df1ec28 | alpha_tetrahedron | 16 | 1.000 | 0.0012411946518617026 | 0.9610956938953713 | 0.9964356639283001 | 0.9995698279351931 | 0.0625 |
| 43ae573f9658f58eab7c8d28677ed7d2197578a5d495b446600f719da915fd2a | alpha_tetrahedron | 16 | 1.000 | 0.17076315452405394 | 0.9503892839557306 | 0.9935847679115858 | 0.9991391539401335 | 0.125 |
| 030c676b19bfbf07adcf01ce27e8a6ea56f653d7ec39539ffb5bccef7ca459e9 | alpha_tetrahedron | 16 | 1.000 | 0.2689061594849121 | 0.9239208152601153 | 0.9940294335822211 | 0.7496915081376576 | 0.125 |
| 1b8a1e4f8f6895c64763be9fe35453d33a02eb777bdd5d40d848b1dc06217bd7 | atomic_nucleus_heavy | 16 | 1.000 | 0.0006899097051531859 | 0.9718824984610701 | 0.995031375852118 | 0.9993474129947345 | 0.0 |
| 338a5769e088089c8f3aa8f984cd0bd1d3e7b168e9a43886f5a07abefaadf0cf | alpha_tetrahedron | 16 | 1.000 | 0.009897047242126273 | 0.9320958825968415 | 0.9925564828816315 | 0.9989688726039001 | 0.0 |
| 1e358bbbb441a290981db5160efb882c748891354b2b0a3b9fca10a346c5a06c | atomic_nucleus_heavy | 16 | 1.000 | 0.003987800576461561 | 0.9265773265922663 | 0.9967942420548489 | 0.8330501555199762 | 0.0 |
| b9bc90aa109f4c6cd594b078a0f791d6fd1ce89df0ea6ab5268e1805a0c934c8 | alpha_tetrahedron | 16 | 1.000 | 0.0023478787682026507 | 0.9497774688858196 | 0.9941727026006124 | 0.9992238667769224 | 0.0625 |
| 965f5e9383ae294ad33838edd6a804ddc217e06e54c4866491f4193708669795 | alpha_tetrahedron | 16 | 1.000 | 0.18063049300640135 | 0.977626242581686 | 0.996671711971284 | 0.9995967318216479 | 0.125 |
| 1a212445cd7ec1db3f2a2f06e60bc9d870c91a7e5df30cf74d764fd505083aab | alpha_tetrahedron | 16 | 1.000 | 0.23277206875891068 | 0.9271604454607846 | 0.9940944595657181 | 0.7497178492623539 | 0.0 |
| eeda6202a9396fca2613c580c94a48865814e224a7f8d92f0098fabe927cfcad | alpha_tetrahedron | 16 | 1.000 | 0.15926060054990115 | 0.963757262821012 | 0.9963464831370683 | 0.9995621660877796 | 0.0625 |

## Top Species (Detailed)
| species_id | assignment | edge_weights | seed_stability | n_trials | n_viable | best_params | best_metrics |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3f6a095d0c7f5640a2c7aaf0b0ce001be0faa43143e7ebbdd43831930b9d83ad | `["meson_d_star_zero_block_0001","unknown_block_0008","unknown_block_0013","unknown_block_0072"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.7163435737836639,"kappa_global":0.3,"tau_field":78.8634624070796,"sigma0":0.19430084944950754,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9961868426007612,"Z_final_abs":0.10913749207806797,"R_mean_lastW":0.9959783792429342,"phase_var_lastW":0.0001213816166814149,"edge_phase_diff_mean_lastW":0.1294765171093933,"edge_phase_diff_std_lastW":0.06864156969852399,"node_omega_mean_lastW":[0.12194776574020388,0.12243209342407106,0.12302990233716198,0.12341147974039383],"node_omega_std_lastW":[0.008102078489387,0.007162184660493563,0.011514753907063201,0.009556767270743198],"omega_eff":0.12270658628414507,"omega_eff_method":"rms","PE_tick_norm":0.9196707863186454,"QualityLock":0.9991529411161281,"entropy_quality":0.9935793353036735,"memory_score_k10":0.914037256277396,"E_local_final":-2.838359932001433,"E_local_mean_lastW":-2.8343924217027903,"E_local_min_lastW":-2.8405672436219307,"E_local_max_lastW":-2.829993481177321,"H_block_mean":0.006420664696326531}` |
| 494201c40628c951eed0bf4f0cb23a93248d93c759ad9a0a7f9fd9817fe6ccc4 | `["delta_1950_block_0010","unknown_block_0076","unknown_block_0120","unknown_block_0154"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.33504146938865753,"kappa_global":0.3,"tau_field":114.21243865603915,"sigma0":0.29563680397559045,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9943200439277938,"Z_final_abs":0.7149498388665715,"R_mean_lastW":0.9933354243164756,"phase_var_lastW":0.00035602389816791435,"edge_phase_diff_mean_lastW":0.14617583644725302,"edge_phase_diff_std_lastW":0.11945594604027242,"node_omega_mean_lastW":[-0.0031058483047289834,-0.0035795396915641745,-0.002927329570579068,-0.0027395456325058675],"node_omega_std_lastW":[0.012703272237098669,0.017371457799715845,0.011064566248913605,0.014394449428590918],"omega_eff":0.0031037786157698108,"omega_eff_method":"rms","PE_tick_norm":0.9108853979067582,"QualityLock":0.99955433730431,"entropy_quality":0.9965052636295032,"memory_score_k10":0.968376511180063,"E_local_final":-1.316765200935905,"E_local_mean_lastW":-1.3162611781238927,"E_local_min_lastW":-1.3234423257112766,"E_local_max_lastW":-1.3105917453287732,"H_block_mean":0.003494736370496838}` |
| 6d2ea79077de856b9229731951054819689e253642d0cf8bec5b9dcd5c414b49 | `["delta_1950_block_0003","meson_ds_block_0003","unknown_block_0120","unknown_block_0151"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.5308354041672355,"kappa_global":0.3,"tau_field":43.47629824891934,"sigma0":0.3305806592462155,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9930516029777791,"Z_final_abs":0.42804111421152524,"R_mean_lastW":0.9937768605345842,"phase_var_lastW":0.00029189860294397796,"edge_phase_diff_mean_lastW":0.162485512299326,"edge_phase_diff_std_lastW":0.08278490184621146,"node_omega_mean_lastW":[-0.045011231034789635,-0.04761423983231189,-0.0475986103717428,-0.04536572087609832],"node_omega_std_lastW":[0.007681374964088688,0.014067395292271884,0.014170500620026555,0.01392615583811135],"omega_eff":0.0464133684782875,"omega_eff_method":"rms","PE_tick_norm":0.9020402170930348,"QualityLock":0.7497272189855135,"entropy_quality":0.994708248036853,"memory_score_k10":0.9437878163304739,"E_local_final":-2.0822136831488494,"E_local_mean_lastW":-2.088208549525703,"E_local_min_lastW":-2.097575215999001,"E_local_max_lastW":-2.0821499317766006,"H_block_mean":0.005291751963146963}` |
| 4fd1f9aed7983467ed588821681d7ed63de2ba0d9e683e9529798e470e2f8726 | `["unknown_block_0101","unknown_block_0152","unknown_block_0154","unknown_block_0167"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.4659711867486819,"kappa_global":0.3,"tau_field":158.458277320059,"sigma0":0.15638544004299265,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9815662331606115,"Z_final_abs":0.09974789526459148,"R_mean_lastW":0.9810270148265909,"phase_var_lastW":8.80656181380186e-05,"edge_phase_diff_mean_lastW":0.26504856539525307,"edge_phase_diff_std_lastW":0.1768143947044915,"node_omega_mean_lastW":[0.056315846615856764,0.05552688434466434,0.05478487371779968,0.05548975454278087],"node_omega_std_lastW":[0.007865947637475246,0.009400518952171732,0.009405938322864028,0.006352398482207422],"omega_eff":0.05553198338025521,"omega_eff_method":"rms","PE_tick_norm":0.8808783075121768,"QualityLock":0.9997222830375031,"entropy_quality":0.9975566889586758,"memory_score_k10":0.9459369733421765,"E_local_final":-1.7662306321568755,"E_local_mean_lastW":-1.7705006862663715,"E_local_min_lastW":-1.7796391525311714,"E_local_max_lastW":-1.7662306321568755,"H_block_mean":0.0024433110413242076}` |
| f30970c6d5f94b36e0117ad2daf2105d237cfe16024fa9973d235e77b8d0d631 | `["unknown_block_0008","unknown_block_0076","unknown_block_0086","unknown_block_0120"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.7226734157540157,"kappa_global":0.3,"tau_field":121.86700964168435,"sigma0":0.1698521515560229,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9994946749615594,"Z_final_abs":0.7731919973913446,"R_mean_lastW":0.9993168827615001,"phase_var_lastW":0.00010988170822589849,"edge_phase_diff_mean_lastW":0.0527155187757239,"edge_phase_diff_std_lastW":0.029414714661776357,"node_omega_mean_lastW":[-0.0018098276244760008,-0.0008202838035015846,-0.001938560039745521,-0.0015812301175245874],"node_omega_std_lastW":[0.012017200541684345,0.01390089926461483,0.010403823852105037,0.006373834938080712],"omega_eff":0.0015973920355432825,"omega_eff_method":"rms","PE_tick_norm":0.9289569645812246,"QualityLock":0.9992769002695412,"entropy_quality":0.9944086665706324,"memory_score_k10":0.9513143504117239,"E_local_final":-2.8856522836469103,"E_local_mean_lastW":-2.885320529783392,"E_local_min_lastW":-2.887045548802131,"E_local_max_lastW":-2.8832702093611453,"H_block_mean":0.0055913334293676105}` |
| bceac9e2eeb9ccd1c7ae2884f6ce198af5de0b3693350d714f1d6866ed5c1c92 | `["sigma_c_2520_block_0001","unknown_block_0050","xi_c_plus_block_0001","xi_c_plus_block_0001"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.6154389247758345,"kappa_global":0.3,"tau_field":111.05869719662584,"sigma0":0.4650961469934173,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9951725985955755,"Z_final_abs":0.005378870860743852,"R_mean_lastW":0.9943590491782723,"phase_var_lastW":0.0007408901934126766,"edge_phase_diff_mean_lastW":0.14178944785384337,"edge_phase_diff_std_lastW":0.1002249484060919,"node_omega_mean_lastW":[1.5014264668199853,1.500645070243823,1.4998943009056322,1.4987517255821043],"node_omega_std_lastW":[0.026389992952272963,0.030416719318507503,0.022690607760620866,0.020685821517624565],"omega_eff":1.5001797151457525,"omega_eff_method":"rms","PE_tick_norm":0.9416028803251111,"QualityLock":0.9990893798580697,"entropy_quality":0.9931723532454845,"memory_score_k10":0.8629608447546234,"E_local_final":-2.4251738809559984,"E_local_mean_lastW":-2.4248180431182935,"E_local_min_lastW":-2.436383838509148,"E_local_max_lastW":-2.4096389320509237,"H_block_mean":0.006827646754515488}` |
| 508a642cd35ad53445734411a3aa3a5b2fa04c644ad82b0ce68297bd8ffea4b3 | `["unknown_block_0005","unknown_block_0014","unknown_block_0015","unknown_block_0141"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.6558532301560426,"kappa_global":0.3,"tau_field":148.9502247260504,"sigma0":0.22298295420800662,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9941588829556416,"Z_final_abs":0.015312061918533145,"R_mean_lastW":0.9935847338370045,"phase_var_lastW":0.00017878765643061334,"edge_phase_diff_mean_lastW":0.15055439049563296,"edge_phase_diff_std_lastW":0.10783496139432829,"node_omega_mean_lastW":[0.28449359620268105,0.2839560877053038,0.28391308091553774,0.2833978664218768],"node_omega_std_lastW":[0.01247791379702506,0.010160062836810058,0.009185069869308237,0.013324759773976234],"omega_eff":0.2839404225505154,"omega_eff_method":"rms","PE_tick_norm":0.9192467214627367,"QualityLock":0.9992329525922726,"entropy_quality":0.9940087418059002,"memory_score_k10":0.9289449185826243,"E_local_final":-2.578697111953598,"E_local_mean_lastW":-2.5784506814896453,"E_local_min_lastW":-2.5852601147023404,"E_local_max_lastW":-2.572419349909368,"H_block_mean":0.0059912581940998084}` |
| c92e9b1ff1f22367ce0796cdc82ca334185bf125885e7f8b4e4eb856cb10f395 | `["unknown_block_0029","unknown_block_0107","unknown_block_0112","unknown_block_0131"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.6737204797405495,"kappa_global":0.3,"tau_field":103.102150704933,"sigma0":0.17897884498611039,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9832078777390795,"Z_final_abs":0.1405450281513742,"R_mean_lastW":0.9827645394795324,"phase_var_lastW":0.00012664612820880404,"edge_phase_diff_mean_lastW":0.2642906405144352,"edge_phase_diff_std_lastW":0.14966779096820404,"node_omega_mean_lastW":[0.06904905727904072,0.06826164816757946,0.06823921626170504,0.06887582107977228],"node_omega_std_lastW":[0.009299460304768165,0.012806848462086773,0.007990752963849533,0.007691415562988034],"omega_eff":0.0686073871516457,"omega_eff_method":"rms","PE_tick_norm":0.9370490155043795,"QualityLock":0.9995277682321222,"entropy_quality":0.9961864897988684,"memory_score_k10":0.919932569746522,"E_local_final":-2.57150618435679,"E_local_mean_lastW":-2.571847118442424,"E_local_min_lastW":-2.5813983795401,"E_local_max_lastW":-2.5622504299879485,"H_block_mean":0.003813510201131655}` |
| 642e1b8f4381da661d23df3794df8b306ecc591ffc9c2b0d350fee0e10e0a2f6 | `["delta_1920_block_0001","delta_1950_block_0002","unknown_block_0006","unknown_block_0120"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.7355140745339748,"kappa_global":0.3,"tau_field":74.14119916302943,"sigma0":0.3738712800455629,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9955775591501926,"Z_final_abs":0.08962957135834786,"R_mean_lastW":0.9965123930927675,"phase_var_lastW":0.0004738155857804671,"edge_phase_diff_mean_lastW":0.12108482413548102,"edge_phase_diff_std_lastW":0.06289122295815397,"node_omega_mean_lastW":[-0.13696088474314724,-0.13651199352940288,-0.13472663819076938,-0.1363513634710575],"node_omega_std_lastW":[0.017601408197509386,0.018120232467721004,0.02180654091281116,0.026428850227212492],"omega_eff":0.1361403409037897,"omega_eff_method":"rms","PE_tick_norm":0.9305369938390297,"QualityLock":0.9992170811164297,"entropy_quality":0.9941589601599755,"memory_score_k10":0.9472985605062187,"E_local_final":-2.920076394140315,"E_local_mean_lastW":-2.9154422710494527,"E_local_min_lastW":-2.926254657284976,"E_local_max_lastW":-2.90476539708875,"H_block_mean":0.005841039840024491}` |
| 661cdadcfc5832590f909da4abedd86faac9a0b0ad33bb002f1721ef8d7a9d97 | `["delta_1920_block_0005","unknown_block_0107","unknown_block_0151","unknown_block_0126","unknown_block_0008","unknown_block_0042"]` | `null` | 1.000 | 16 | 16 | `{"dt":1.0,"T_ticks":200,"W":20,"K_local":0.6368076702483088,"kappa_global":0.3,"tau_field":123.33700252467604,"sigma0":0.1646611597943483,"sigma_tc":60.0,"sigma_theta_init":0.5}` | `{"R_final":0.9843730709373026,"Z_final_abs":0.7718333849095288,"R_mean_lastW":0.9844829692712374,"phase_var_lastW":0.00012350444672058026,"edge_phase_diff_mean_lastW":0.22642755576068288,"edge_phase_diff_std_lastW":0.12850456062048854,"node_omega_mean_lastW":[-0.0003873550313911485,-0.00039742643200138685,-0.0017230042782031025,-0.0011082438662278467,-0.0006134562053327835,-0.0003879567270455721],"node_omega_std_lastW":[0.014482928910484541,0.00957768597452964,0.011414622912775414,0.011008222627651273,0.006509780098118915,0.009340849662859682],"omega_eff":0.0009157673318822527,"omega_eff_method":"rms","PE_tick_norm":0.921324585053118,"QualityLock":0.9996863890394297,"entropy_quality":0.9973474648232435,"memory_score_k10":0.9570637590618014,"E_local_final":-3.693190785561246,"E_local_mean_lastW":-3.6925746687254097,"E_local_min_lastW":-3.701146551201991,"E_local_max_lastW":-3.68344045066893,"H_block_mean":0.0026525351767564044}` |

## Angels
- count: 687
- top_ids:
  - 3f6a095d0c7f5640a2c7aaf0b0ce001be0faa43143e7ebbdd43831930b9d83ad seed_stability=1.0 omega_eff=0.12270658628414507 memory=0.914037256277396 entropy=0.9935793353036735 QualityLock=0.9991529411161281
  - 494201c40628c951eed0bf4f0cb23a93248d93c759ad9a0a7f9fd9817fe6ccc4 seed_stability=1.0 omega_eff=0.0031037786157698108 memory=0.968376511180063 entropy=0.9965052636295032 QualityLock=0.99955433730431
  - 6d2ea79077de856b9229731951054819689e253642d0cf8bec5b9dcd5c414b49 seed_stability=1.0 omega_eff=0.0464133684782875 memory=0.9437878163304739 entropy=0.994708248036853 QualityLock=0.7497272189855135
  - 4fd1f9aed7983467ed588821681d7ed63de2ba0d9e683e9529798e470e2f8726 seed_stability=1.0 omega_eff=0.05553198338025521 memory=0.9459369733421765 entropy=0.9975566889586758 QualityLock=0.9997222830375031
  - f30970c6d5f94b36e0117ad2daf2105d237cfe16024fa9973d235e77b8d0d631 seed_stability=1.0 omega_eff=0.0015973920355432825 memory=0.9513143504117239 entropy=0.9944086665706324 QualityLock=0.9992769002695412
  - 508a642cd35ad53445734411a3aa3a5b2fa04c644ad82b0ce68297bd8ffea4b3 seed_stability=1.0 omega_eff=0.2839404225505154 memory=0.9289449185826243 entropy=0.9940087418059002 QualityLock=0.9992329525922726
  - c92e9b1ff1f22367ce0796cdc82ca334185bf125885e7f8b4e4eb856cb10f395 seed_stability=1.0 omega_eff=0.0686073871516457 memory=0.919932569746522 entropy=0.9961864897988684 QualityLock=0.9995277682321222
  - 642e1b8f4381da661d23df3794df8b306ecc591ffc9c2b0d350fee0e10e0a2f6 seed_stability=1.0 omega_eff=0.1361403409037897 memory=0.9472985605062187 entropy=0.9941589601599755 QualityLock=0.9992170811164297
  - 661cdadcfc5832590f909da4abedd86faac9a0b0ad33bb002f1721ef8d7a9d97 seed_stability=1.0 omega_eff=0.0009157673318822527 memory=0.9570637590618014 entropy=0.9973474648232435 QualityLock=0.9996863890394297
  - 82df9f6241c8fa4d600cd77d742d4a689d408bfca19170c6a8b4e94a1df1ec28 seed_stability=1.0 omega_eff=0.0012411946518617026 memory=0.9610956938953713 entropy=0.9964356639283001 QualityLock=0.9995698279351931

## Config Snapshot
```json
{
  "schema_version": "ola2_structure_explorer_v3",
  "inputs": {
    "blocks_json": "data/processed/ola1/simple_blocks.json",
    "templates_json": "data/raw/compound_templates_v3.json",
    "species_catalog_jsonl": "data/processed/ola2-v3/species_catalog.jsonl",
    "blocks_mode": "ola1_blocks"
  },
  "targets": [
    {
      "name": "atomic_search_all",
      "templates": [
        "alpha_tetrahedron",
        "atomic_nucleus_heavy"
      ],
      "allowed_block_families": [],
      "budget_evals": 200000
    }
  ],
  "engine_defaults": {
    "dt": 1,
    "T_ticks": 200,
    "W": 20,
    "K_local": 0.45,
    "kappa_global": 0.3,
    "tau_field": 120,
    "sigma0": 0.3,
    "sigma_tc": 60,
    "sigma_theta_init": 0.5
  },
  "engine_variation": {
    "enabled": true,
    "mode": "bin_sample",
    "bins": {
      "K_local_edges": [
        0.2,
        0.4,
        0.6,
        0.8
      ],
      "tau_field_edges": [
        40,
        80,
        120,
        160,
        240
      ],
      "sigma0_edges": [
        0.1,
        0.3,
        0.5
      ]
    }
  },
  "coupling_mode": {
    "mode": "absolute"
  },
  "tagging": {
    "R_mean_lastW_min": 0.8,
    "phase_var_lastW_max": 0.05,
    "memory_score_k10_min": 0.0,
    "quality_lock_min": 0.75,
    "viability_mode": "hard_viable_soft_memory"
  },
  "search_policy": {
    "phase1_fraction": 0.4,
    "phase2_fraction": 0.6,
    "phase1": {
      "prefer_novel_structures": true,
      "template_balance": "round_robin"
    },
    "phase2": {
      "seed_repeats_per_structure": 15,
      "param_neighbor_bins": 3
    },
    "priority_scoring": {
      "score": "R_mean_lastW + 0.6*memory_score_k10 - 1.5*phase_var_lastW"
    }
  }
}
```

## Templates Snapshot
```json
[
  {
    "name": "singlet",
    "type": "elementary",
    "nodes": 1,
    "edges": []
  },
  {
    "name": "meson_dimer",
    "type": "meson_complex",
    "nodes": 2,
    "edges": [
      [
        0,
        1
      ]
    ]
  },
  {
    "name": "baryon_triangle",
    "type": "baryon",
    "nodes": 3,
    "edges": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ]
    ]
  },
  {
    "name": "alpha_tetrahedron",
    "type": "nucleus",
    "nodes": 4,
    "edges": [
      [
        0,
        1
      ],
      [
        0,
        2
      ],
      [
        0,
        3
      ],
      [
        1,
        2
      ],
      [
        1,
        3
      ],
      [
        2,
        3
      ]
    ],
    "notes": "Geometr\u00eda fundamental del n\u00facleo de Helio (4 nodos)."
  },
  {
    "name": "atomic_nucleus_heavy",
    "type": "atom_core",
    "nodes": 6,
    "edges": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ],
      [
        3,
        4
      ],
      [
        4,
        5
      ],
      [
        5,
        3
      ],
      [
        0,
        3
      ],
      [
        1,
        4
      ],
      [
        2,
        5
      ]
    ],
    "notes": "Estructura de 6 nodos (Prisma Triangular) para b\u00fasqueda de n\u00facleos pesados."
  }
]
```
