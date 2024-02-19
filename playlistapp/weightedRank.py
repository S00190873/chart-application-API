def rank_songs(charts, weights):
    # Initialize a combined list for all charts processed
    combined_charts = []

    # Process each chart with its corresponding weight
    for chart, weight in zip(charts, weights):
        chart_processed = [
            (entry["Position"], entry["Songname"], entry["Artist"], weight, 
             ((len(chart) + 1 - entry["Position"]) * weight) / len(chart))
            for entry in chart
        ]
        combined_charts.extend(chart_processed)

    # Create a dictionary to aggregate scores and counts for each song
    merged_entries = {}
    for position, name, artist, weight, score in combined_charts:
        key = (name, artist)
        if key in merged_entries:
            merged_entries[key][2] += weight  # Add weight
            merged_entries[key][3] += score  # Add score
        else:
            merged_entries[key] = [name, artist, weight, score]

    # Convert the merged entries dictionary to a list
    merged_list = list(merged_entries.values())

    # Sort the merged list by score and then by weight
    sorted_list = sorted(merged_list, key=lambda x: (-x[3], -x[2]))

    # Construct the final list
    final_list = [(i, song[0], song[1], song[3]) for i, song in enumerate(sorted_list, start=1)]

    return final_list
