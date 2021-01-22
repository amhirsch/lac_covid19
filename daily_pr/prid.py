"""Every news release from Los Angeles County Department of Public Health
    is identified by a unique PRID. The map associate a date and the
    corresponding COVID-19 daily news release.
"""

PRID = {
    '2020-03-30': 2289, '2020-03-31': 2290, '2020-04-01': 2291,
    '2020-04-02': 2292, '2020-04-03': 2294, '2020-04-04': 2297,
    '2020-04-05': 2298, '2020-04-06': 2300, '2020-04-07': 2302,
    '2020-04-08': 2304, '2020-04-09': 2307, '2020-04-10': 2309,
    '2020-04-11': 2311, '2020-04-12': 2312, '2020-04-13': 2314,
    '2020-04-14': 2317, '2020-04-15': 2319, '2020-04-16': 2321,
    '2020-04-17': 2323, '2020-04-18': 2325, '2020-04-19': 2326,
    '2020-04-20': 2329, '2020-04-21': 2331, '2020-04-22': 2333,
    '2020-04-23': 2336, '2020-04-24': 2337, '2020-04-25': 2341,
    '2020-04-26': 2343, '2020-04-27': 2345, '2020-04-28': 2347,
    '2020-04-29': 2349, '2020-04-30': 2352, '2020-05-01': 2353,
    '2020-05-02': 2355, '2020-05-03': 2356, '2020-05-04': 2357,
    '2020-05-05': 2359, '2020-05-06': 2361, '2020-05-07': 2362,
    '2020-05-08': 2365, '2020-05-09': 2367, '2020-05-10': 2369,
    '2020-05-11': 2370, '2020-05-12': 2373, '2020-05-13': 2375,
    '2020-05-14': 2377, '2020-05-15': 2380, '2020-05-16': 2381,
    '2020-05-17': 2382, '2020-05-18': 2384, '2020-05-19': 2386,
    '2020-05-20': 2389, '2020-05-21': 2391, '2020-05-22': 2393,
    '2020-05-23': 2394, '2020-05-24': 2399, '2020-05-25': 2400,
    '2020-05-26': 2403, '2020-05-27': 2406, '2020-05-28': 2408,
    '2020-05-29': 2409, '2020-05-30': 2411, '2020-05-31': 2412,
    '2020-06-01': 2413, '2020-06-02': 2419, '2020-06-03': 2422,
    '2020-06-04': 2423, '2020-06-05': 2426, '2020-06-06': 2428,
    '2020-06-07': 2429, '2020-06-08': 2430, '2020-06-09': 2432,
    '2020-06-10': 2436, '2020-06-11': 2438, '2020-06-12': 2440,
    '2020-06-13': 2442, '2020-06-14': 2443, '2020-06-15': 2445,
    '2020-06-16': 2447, '2020-06-17': 2449, '2020-06-18': 2451,
    '2020-06-19': 2452, '2020-06-20': 2455, '2020-06-21': 2456,
    '2020-06-22': 2458, '2020-06-23': 2462, '2020-06-24': 2465,
    '2020-06-25': 2467, '2020-06-26': 2469, '2020-06-27': 2470,
    '2020-06-28': 2471, '2020-06-29': 2472, '2020-06-30': 2476,
    '2020-07-01': 2477, '2020-07-02': 2480, '2020-07-06': 2485,
    '2020-07-07': 2487, '2020-07-08': 2489, '2020-07-09': 2492,
    '2020-07-10': 2496, '2020-07-11': 2500, '2020-07-12': 2501,
    '2020-07-13': 2503, '2020-07-14': 2506, '2020-07-15': 2508,
    '2020-07-16': 2510, '2020-07-17': 2514, '2020-07-18': 2516,
    '2020-07-19': 2518, '2020-07-20': 2521, '2020-07-21': 2522,
    '2020-07-22': 2526, '2020-07-23': 2527, '2020-07-24': 2529,
    '2020-07-25': 2531, '2020-07-26': 2533, '2020-07-27': 2535,
    '2020-07-28': 2537, '2020-07-29': 2538, '2020-07-30': 2540,
    '2020-07-31': 2543, '2020-08-01': 2545, '2020-08-02': 2548,
    '2020-08-03': 2550, '2020-08-04': 2551, '2020-08-05': 2556,
    '2020-08-06': 2558, '2020-08-07': 2560, '2020-08-08': 2561,
    '2020-08-09': 2562, '2020-08-10': 2566, '2020-08-11': 2567,
    '2020-08-12': 2571, '2020-08-13': 2575, '2020-08-14': 2577,
    '2020-08-15': 2580, '2020-08-16': 2583, '2020-08-17': 2586,
    '2020-08-18': 2591, '2020-08-19': 2595, '2020-08-20': 2597,
    '2020-08-21': 2600, '2020-08-22': 2603, '2020-08-23': 2605,
    '2020-08-24': 2608, '2020-08-25': 2611, '2020-08-26': 2614,
    '2020-08-27': 2615, '2020-08-28': 2619, '2020-08-29': 2620,
    '2020-08-30': 2623, '2020-08-31': 2625, '2020-09-01': 2628,
    '2020-09-02': 2631, '2020-09-03': 2634, '2020-09-04': 2636,
    '2020-09-05': 2639, '2020-09-06': 2642, '2020-09-07': 2644,
    '2020-09-08': 2646, '2020-09-09': 2649, '2020-09-10': 2655,
    '2020-09-11': 2657, '2020-09-12': 2660, '2020-09-13': 2663,
    '2020-09-14': 2665, '2020-09-15': 2668, '2020-09-16': 2671,
    '2020-09-17': 2675, '2020-09-18': 2679, '2020-09-19': 2681,
    '2020-09-20': 2682, '2020-09-21': 2685, '2020-09-22': 2689,
    '2020-09-23': 2690, '2020-09-24': 2694, '2020-09-25': 2699,
    '2020-09-26': 2702, '2020-09-27': 2705, '2020-09-28': 2708,
    '2020-09-29': 2716, '2020-09-30': 2717, '2020-10-01': 2719,
    '2020-10-02': 2722, '2020-10-03': 2725, '2020-10-04': 2726,
    '2020-10-05': 2728, '2020-10-06': 2731, '2020-10-07': 2734,
    '2020-10-08': 2737, '2020-10-09': 2738, '2020-10-10': 2740,
    '2020-10-11': 2741, '2020-10-12': 2744, '2020-10-13': 2745,
    '2020-10-14': 2749, '2020-10-15': 2751, '2020-10-16': 2754,
    '2020-10-17': 2758, '2020-10-18': 2759, '2020-10-19': 2760,
    '2020-10-20': 2763, '2020-10-21': 2765, '2020-10-22': 2766,
    '2020-10-23': 2769, '2020-10-24': 2770, '2020-10-25': 2771,
    '2020-10-26': 2772, '2020-10-27': 2776, '2020-10-28': 2777,
    '2020-10-29': 2780, '2020-10-30': 2783, '2020-10-31': 2785,
    '2020-11-01': 2786, '2020-11-02': 2787, '2020-11-03': 2790,
    '2020-11-04': 2791, '2020-11-05': 2792, '2020-11-06': 2795,
    '2020-11-07': 2796, '2020-11-08': 2798, '2020-11-09': 2800,
    '2020-11-10': 2801, '2020-11-11': 2802, '2020-11-12': 2805,
    '2020-11-13': 2806, '2020-11-14': 2807, '2020-11-15': 2808,
    '2020-11-16': 2809, '2020-11-17': 2812, '2020-11-18': 2813,
    '2020-11-19': 2815, '2020-11-20': 2816, '2020-11-21': 2818,
    '2020-11-22': 2819, '2020-11-23': 2820, '2020-11-24': 2821,
    '2020-11-25': 2828, '2020-11-26': 2829, '2020-11-27': 2830,
    '2020-11-28': 2831, '2020-11-29': 2832, '2020-11-30': 2834,
    '2020-12-01': 2835, '2020-12-02': 2836, '2020-12-03': 2838,
    '2020-12-04': 2841, '2020-12-05': 2843, '2020-12-06': 2844,
    '2020-12-07': 2845, '2020-12-08': 2847, '2020-12-09': 2848,
    '2020-12-10': 2849, '2020-12-11': 2853, '2020-12-12': 2854,
    '2020-12-13': 2855, '2020-12-14': 2856, '2020-12-15': 2860,
    '2020-12-16': 2863, '2020-12-17': 2864, '2020-12-18': 2865,
    '2020-12-19': 2866, '2020-12-20': 2868, '2020-12-21': 2869,
    '2020-12-22': 2870, '2020-12-23': 2872, '2020-12-24': 2877,
    '2020-12-26': 2880, '2020-12-27': 2881, '2020-12-28': 2883,
    '2020-12-29': 2885, '2020-12-30': 2887, '2020-12-31': 2891,
    '2021-01-01': 2893, '2021-01-02': 2894, '2021-01-03': 2895,
    '2021-01-04': 2896, '2021-01-05': 2897, '2021-01-06': 2899,
    '2021-01-07': 2904, '2021-01-08': 2904, '2021-01-09': 2905,
    '2021-01-10': 2906, '2021-01-11': 2908, '2021-01-12': 2909,
    '2021-01-13': 2912, '2021-01-14': 2914, '2021-01-15': 2917,
    '2021-01-16': 2918, '2021-01-17': 2921, '2021-01-18': 2922,
    '2021-01-19': 2923, '2021-01-20': 2924, '2021-01-21': 2925,
}
