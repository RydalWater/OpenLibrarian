def remove_dups_on_id(events: list = None, event_type: str = "library") -> None:
    """Remove duplicate events from a list of events."""
    if events is None:
        print(f"No {event_type} events to process.")
        return []
    
    # Order events by id and created date 
    events = sorted(events, key=lambda event: (event.tags().identifier(), event.created_at().as_secs()), reverse=True)
    
    # Remove duplicates by identifier
    seen_ids = set()
    unique_events = []
    for event in events:
        identifier = event.tags().identifier()
        if identifier not in seen_ids:
            seen_ids.add(identifier)
            unique_events.append(event)
    if events != unique_events:
        print(f"Removed {len(events) - len(unique_events)} duplicate {event_type} events.")

    return unique_events