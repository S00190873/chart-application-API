def rank_songs(globalChart, countryChart, GlobalWeight, CountryWeight):
  # Flatten the charts into a list of tuples for easier processing
    global_chart_processed = [(entry["Position"], entry["Songname"], entry["Artist"], GlobalWeight) for entry in globalChart]
    country_chart_processed = [(entry["Position"], entry["Songname"], entry["Artist"], CountryWeight) for entry in countryChart]

    # Calculate the length of each relevant list
    N_global = float(len(global_chart_processed))
    N_country = float(len(country_chart_processed))
    

    # Calculate these values once to avoid redundant calculations
    N_global_plus_1 = N_global + 1
    N_country_plus_1 = N_country + 1

    # Correct the list comprehensions
    global_list_with_values = [
        (position, name, artist, GlobalWeight, ((N_global_plus_1 - position) * GlobalWeight) / N_global)
        for (position, name, artist, GlobalWeight) in global_chart_processed
    ]

    country_list_with_values = [
        (position, name, artist, CountryWeight, ((N_country_plus_1 - position) * CountryWeight) / N_country)
        for (position, name, artist, CountryWeight) in country_chart_processed
    ]

    # Combine both charts
    combined_charts = global_list_with_values + country_list_with_values

    # Create a dictionary to aggregate scores and counts
    merged_entries = {}

    for position, name, artist, weight, rank in combined_charts:
        key = (name, artist)
        if key in merged_entries:
            merged_entries[key][2] += weight  # Add rank values
            merged_entries[key][3] += rank  # Add rank values

        else:
            # Create a new entry
            merged_entries[key] = [name, artist,  weight, rank]

    # Convert the merged entries dictionary to a list
    merged_list = [entry for entry in merged_entries.values()]

    # Sort the merged list by the fourth value (ranked score) and weight
    sorted_list = sorted(merged_list, key=lambda x: (-x[3], -x[2]))

     # Construct the final list excluding the weight
    final_list = [(i, song[0], song[1], song[3]) for i, song in enumerate(sorted_list, start=1)]

    return final_list