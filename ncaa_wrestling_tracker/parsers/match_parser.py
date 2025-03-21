"""
Match parsing functionality for the NCAA Wrestling Tournament Tracker
"""
import re
from typing import Optional, Dict, Any
from ncaa_wrestling_tracker import config
from ncaa_wrestling_tracker.utils.logging_utils import log_debug, log_problem


def parse_match_result(match_text: str, current_weight: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Parse a single match result text and extract relevant information.
    
    Args:
        match_text: Text describing a match result
        current_weight: Current weight class being processed
        
    Returns:
        Dictionary with match information or None if parsing fails
    """
    # Check if any problematic wrestler is in this line first
    for wrestler in config.PROBLEM_WRESTLERS:
        if wrestler.lower() in match_text.lower():
            log_problem(f"Found problem wrestler match: {match_text}")
    
    # Check if this is a placement match
    is_placement_match = False
    placement_pattern = r"(1st|2nd|3rd|4th|5th|6th|7th|8th) Place Match"
    placement_match = re.search(placement_pattern, match_text)
    if placement_match:
        is_placement_match = True
        log_debug(f"Found placement match: {match_text}")
    
    # Special pattern for placement matches
    if is_placement_match:
        return _parse_placement_match(match_text, current_weight)
    else:
        return _parse_regular_match(match_text, current_weight)


def _parse_placement_match(match_text: str, current_weight: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Parse a placement match result
    
    Args:
        match_text: Text describing a placement match
        current_weight: Current weight class
        
    Returns:
        Dictionary with match information or None if parsing fails
    """
    placement_pattern_full = r"(1st|2nd|3rd|4th|5th|6th|7th|8th) Place Match - (.*?) \((.*?)\)(.*?)won (by|in) (.*?) over (.*?) \((.*?)\)(.*)"
    
    match = re.search(placement_pattern_full, match_text)
    if not match:
        log_debug(f"Failed to parse placement match: {match_text}")
        return None
        
    placement = match.group(1)
    winner_name = match.group(2).strip()
    winner_school = match.group(3).strip()
    win_type_full = match.group(6).strip()
    loser_name = match.group(7).strip()
    loser_school = match.group(8).strip()
    
    # Map the placement string to integers
    placement_map = {"1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5, "6th": 6, "7th": 7, "8th": 8}
    placement_num = placement_map.get(placement)
    
    # Determine the placements for winner and loser
    if placement == "1st":
        winner_placement = 1
        loser_placement = 2
    elif placement == "3rd":
        winner_placement = 3
        loser_placement = 4
    elif placement == "5th":
        winner_placement = 5
        loser_placement = 6
    elif placement == "7th":
        winner_placement = 7
        loser_placement = 8
    else:
        # For other placements, we can't determine both precisely
        winner_placement = None
        loser_placement = None
    
    # Parse the win type and bonus points
    win_type, bonus_points = _parse_win_type(win_type_full, match_text)
    
    # Return placement match info
    return {
        'is_placement_match': True,
        'placement_match': placement,
        'winner_name': winner_name,
        'winner_school': winner_school,
        'winner_placement': winner_placement,
        'loser_name': loser_name,
        'loser_school': loser_school,
        'loser_placement': loser_placement,
        'weight': current_weight,
        'win_type': win_type,
        'win_type_full': win_type_full,
        'advancement_points': 0.0,  # No advancement points for placement matches
        'bonus_points': bonus_points,
        'total_points': bonus_points,  # Only bonus points in placement matches
        'match_text': match_text
    }


def _parse_regular_match(match_text: str, current_weight: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Parse a regular (non-placement) match result
    
    Args:
        match_text: Text describing a match
        current_weight: Current weight class
        
    Returns:
        Dictionary with match information or None if parsing fails
    """
    # Regular match pattern - more flexible with "won by" and "won in" variations
    pattern = r"(Champ|Cons)\. Round (\d+) - (.*?) \((.*?)\)(.*?)won (by|in) (.*?) over (.*?) \((.*?)\)(.*)"
    
    match = re.search(pattern, match_text)
    if not match:
        # Try a more lenient pattern as backup
        backup_pattern = r"(Champ|Cons)\. Round (\d+) - (.*?) \((.*?)\)(.*?)won.* over (.*?) \((.*?)\)(.*)"
        backup_match = re.search(backup_pattern, match_text)
        
        if backup_match:
            log_debug(f"Parsed with backup pattern: {match_text}")
            bracket = backup_match.group(1)
            round_num = backup_match.group(2)
            winner_name = backup_match.group(3).strip()
            winner_school = backup_match.group(4).strip()
            # Default win type - will try to detect from full text
            win_type_full = "decision"
            loser_name = backup_match.group(6).strip()
            loser_school = backup_match.group(7).strip()
        else:
            log_debug(f"Failed to parse with all patterns: {match_text}")
            return None
    else:
        # Successful match with primary pattern
        bracket = match.group(1)
        round_num = match.group(2)
        winner_name = match.group(3).strip()
        winner_school = match.group(4).strip()
        win_type_full = match.group(7).strip()
        loser_name = match.group(8).strip()
        loser_school = match.group(9).strip()
    
    # Extract seed info from the match text if available
    winner_seed = None
    winner_seed_num = None
    
    # Look for seed pattern in the match text (after the wrestler's name)
    seed_pattern = r"\(.*?\)\s+(\d+)-\d+\s+(?:\(#(\d+)\))?"
    seed_match = re.search(seed_pattern, match_text)
    if seed_match and seed_match.group(2):
        winner_seed = f"#{seed_match.group(2)}"
        winner_seed_num = int(seed_match.group(2))
    
    # Format the round for tracking
    full_round = f"{bracket} R{round_num}"
    
    # NCAA Scoring Rules for advancement points
    advancement_points = 1.0 if bracket == "Champ" else 0.5
    
    # Parse win type and bonus points
    win_type, bonus_points = _parse_win_type(win_type_full, match_text)
    
    # Double check for specifically problematic formats
    if "(SV-1" in match_text:
        win_type = "SV"
        win_type_full = "sudden victory"
        log_problem(f"SV-1 pattern detected: {match_text}")
    elif "(TB-1" in match_text:
        win_type = "TB"
        win_type_full = "tie breaker"
        log_problem(f"TB-1 pattern detected: {match_text}")
    
    # Calculate total points (advancement + bonus)
    total_points = advancement_points + bonus_points
    
    if win_type in ["SV", "TB"]:
        log_problem(f"Detected {win_type} match: {match_text}")
    
    # Return the parsed match info
    return {
        'is_placement_match': False,
        'bracket': bracket,
        'round_num': int(round_num),
        'full_round': full_round,
        'winner_name': winner_name,
        'winner_school': winner_school,
        'winner_seed': winner_seed,
        'winner_seed_num': winner_seed_num,
        'weight': current_weight,
        'loser_name': loser_name,
        'loser_school': loser_school,
        'win_type': win_type,
        'win_type_full': win_type_full,
        'advancement_points': advancement_points,
        'bonus_points': bonus_points,
        'total_points': total_points,
        'match_text': match_text
    }


def _parse_win_type(win_type_full: str, match_text: str) -> tuple:
    """
    Parse the win type and determine bonus points
    
    Args:
        win_type_full: Full description of win type
        match_text: Full match text for additional context
        
    Returns:
        Tuple of (win_type, bonus_points)
    """
    # Handle different win types - robust detection
    if "tech fall" in win_type_full:
        bonus_points = 1.5
        win_type = "TF"
    elif "major decision" in win_type_full:
        bonus_points = 1.0
        win_type = "MD"
    elif any(x in win_type_full for x in ["fall", "pin"]) and "tech fall" not in win_type_full:
        bonus_points = 2.0
        win_type = "Fall"
    elif any(x in win_type_full for x in ["default", "forfeit", "disqualification", "misconduct"]):
        bonus_points = 2.0
        win_type = "Def/DQ"
    elif "sudden victory" in win_type_full or win_type_full.startswith("sudden victory"):
        bonus_points = 0.0
        win_type = "SV"
    elif "tie breaker" in win_type_full or win_type_full.startswith("tie breaker"):
        bonus_points = 0.0
        win_type = "TB"
    elif "decision" in win_type_full:
        bonus_points = 0.0
        win_type = "Dec"
    else:
        # Check the entire match text for patterns
        if "sudden victory" in match_text or " SV-1 " in match_text or " SV-2 " in match_text or "(SV-1" in match_text:
            bonus_points = 0.0
            win_type = "SV"
        elif "tie breaker" in match_text or " TB-1 " in match_text or " TB-2 " in match_text or "(TB-1" in match_text:
            bonus_points = 0.0
            win_type = "TB"
        else:
            bonus_points = 0.0
            win_type = "Other"
    
    return win_type, bonus_points


def analyze_win_types(results_text: str) -> None:
    """
    Extract and analyze all win type formats in the results
    
    Args:
        results_text: Full text of results
    """
    win_types = set()
    for line in results_text.split('\n'):
        if "won by" in line or "won in" in line:
            # Extract the win type portion
            win_start = line.find("won by ") 
            if win_start == -1:
                win_start = line.find("won in ")
            
            if win_start != -1:
                win_start += 7  # Length of "won by " or "won in "
                win_end = line.find(" over", win_start)
                if win_end != -1:
                    win_type = line[win_start:win_end].strip()
                    win_types.add(win_type)
    
    # Log all win types found
    log_problem("ALL WIN TYPES FOUND:")
    for win_type in sorted(win_types):
        log_problem(f"  - '{win_type}'")


def find_specific_wrestlers(results_text: str, specific_names: list) -> None:
    """
    Find and log all occurrences of specific wrestlers in the results
    
    Args:
        results_text: Full text of results
        specific_names: List of wrestler names to search for
    """
    log_problem("\nSPECIFIC WRESTLER SEARCH:")
    for name in specific_names:
        occurrences = []
        for line in results_text.split('\n'):
            if name in line:
                occurrences.append(line)
        
        log_problem(f"Wrestler '{name}' found in {len(occurrences)} lines:")
        for line in occurrences:
            log_problem(f"  {line}")