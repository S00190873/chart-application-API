from .models import get_riaa_certification_info

def rank_songs(charts, weights):
    max_n = max(len(chart) for chart in charts)
    combined_charts = []

    # Process each chart and combine data
    for chart, weight in zip(charts, weights):
        chart_processed = [
            (
                index + 1,  # Position
                entry["Title"],  # Title
                entry["Artist"],  # Artist
                weight,
                ((max_n + 1 - (index + 1)) * weight) / max_n,  # Score
                entry.get('Description', format_table_name(index + 1, entry.get('TableName', '')))  # Description
            )
            for index, entry in enumerate(chart)
        ]
        combined_charts.extend(chart_processed)

    # Merge entries with the same title and artist
    merged_entries = {}
    for position, title, artist, weight, score, description in combined_charts:
        key = (title, artist)
        if key in merged_entries:
            merged_entries[key][2] += weight
            merged_entries[key][3] += score
            merged_entries[key][4].append(description)
        else:
            merged_entries[key] = [title, artist, weight, score, [description]]

    # Convert merged entries to a list
    merged_list = list(merged_entries.values())

    # Sort the list by score in descending order and by weight as secondary
    sorted_list = sorted(merged_list, key=lambda x: (-x[3], -x[2]))

    final_list = []
    for i, song in enumerate(sorted_list, start=1):
        title, artist, weight, score, descriptions = song
        award, units = get_riaa_certification_info(title, artist)
        formatted_descriptions = descriptions

        if award and units:
            units_in_millions = units  # Units are already in millions as returned by get_riaa_certification_info
            base_units = 500_000  # Base unit is 500,000
            scale_factor = 0.1  # Scale factor for bonus calculation

            # Calculate the multiplier and the bonus
            multiplier = 1.1 + ((units_in_millions * 1_000_000 - base_units) / base_units) * scale_factor
            original_score = score
            score *= multiplier
            bonus = score - original_score

        final_list.append(
            (
                i,  # Rank
                title,  # Title
                artist,  # Artist
                score,  # Adjusted Score
                formatted_descriptions,  # Descriptions as a list
                award,  # RIAA award if applicable
                units,  # Units in millions if applicable
                bonus if award and units else 0  # Include bonus if applicable
            )
        )

    # Sort final list by adjusted score in descending order
    final_list.sort(key=lambda x: -x[3])

    return final_list


def format_table_name(position, table_name):
    parts = table_name.split('_')
    formatted_name = ' '.join(part.capitalize() for part in parts)
    return f"#{position} on {formatted_name}"
