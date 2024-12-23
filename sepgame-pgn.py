import os
import re
import shutil
import platform
import argparse
from tqdm import tqdm
import sys
from typing import List, Dict


def clear_console():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def clear_output_directory():
    output_dir = 'output'
    if os.path.exists(output_dir):
        print('\n\033[91mclearing all old files and folders in the output folder before we start...\033[0m\n')
        total_files = sum(len(files) + len(dirs) for _, dirs, files in os.walk(output_dir))
        if total_files > 0:
            with tqdm(total=total_files, desc="\033[92mDeleting files and folders\033[0m") as pbar:
                for root, dirs, files in os.walk(output_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                        pbar.update(1)
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                        pbar.update(1)
            os.rmdir(output_dir)
        print('\ndone!\n')

def load_pgn_files():
    pgn_files = [f for f in os.listdir() if f.endswith('.pgn')]
    return pgn_files



def convert_to_english_chars(text: str) -> str:
    """
    Convert German, Spanish, French and Portuguese characters to their English equivalents.
    """
    char_map = {
        # German characters
        'ä': 'a', 'ö': 'o', 'ü': 'u', 'ß': 'ss',
        'Ä': 'A', 'Ö': 'O', 'Ü': 'U',
        
        # Spanish characters
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'Ñ': 'N', 'Ü': 'U',
        
        # French characters
        'à': 'a', 'â': 'a', 'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'î': 'i', 'ï': 'i', 'ô': 'o', 'ù': 'u', 'û': 'u', 'ÿ': 'y',
        'ç': 'c',
        'À': 'A', 'Â': 'A', 'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'Î': 'I', 'Ï': 'I', 'Ô': 'O', 'Ù': 'U', 'Û': 'U', 'Ÿ': 'Y',
        'Ç': 'C',
        
        # Portuguese characters
        'ã': 'a', 'õ': 'o', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'ç': 'c',
        'Ã': 'A', 'Õ': 'O', 'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'À': 'A', 'Ç': 'C'
    }
    
    return ''.join(char_map.get(c, c) for c in text)

def parse_pgn(file_content: str) -> List[Dict]:
    # Predefined set of keys that should preserve the full line format
    
    PRESERVE_LINE_KEYS = {
        # Event Information
        'event', 'eventdate', 'eventsponsor', 'eventtype', 'eventrounds', 'eventcountry', 'eventcategory',
        
        # Game Location and Time
        'site', 'date', 'time', 'utctime', 'utcdate',
        
        # Player Information - White
        'white', 'whiteelo', 'whitetitle', 'whiteuscf', 'whitena', 'whitetype', 'whiteteam', 'whiteteamcountry',
        'whiteacpl', 'whitefideid', 'whiteratingdiff', 'whiterd', 'whiterating',
        
        # Player Information - Black
        'black', 'blackelo', 'blacktitle', 'blackuscf', 'blackna', 'blacktype', 'blackteam', 'blackteamcountry',
        'blackacpl', 'blackfideid', 'blackratingdiff', 'blackrd', 'blackrating',
        
        # Game Classification
        'round', 'result', 'eco', 'nic', 'opening', 'variation', 'subvariation',
        
        # Game Control and Setup
        'timecontrol', 'setup', 'fen', 'termination', 'variant', 'mode',
        
        # Game Analysis and Quality
        'annotator', 'beauty', 'plycount', 'sourcequality',
        
        # Tournament Information
        'section', 'stage', 'board', 'table',
        
        # Source Information
        'source', 'sourcetitle', 'sourcedate', 'sourceversion', 'sourceversiondate',
        
        # Additional Game Details
        'clock', 'increment', 'timeseal', 'rated', 'promotion',
        
        # Player Status
        'whitestatus', 'blackstatus', 'whiteactive', 'blackactive',
        
        # Tournament Details
        'tournamenttype', 'tournamentname', 'tournamentdate', 'tournamentrounds',
        
        # Game Specifics
        'gametype', 'gamevariant', 'gamephase', 'gameresult', 'gameduration',
        
        # Time Management
        'whitetime', 'blacktime', 'whiteclock', 'blackclock',
        
        # Rating Information
        'averageelo', 'ratingtype', 'ratingcategory',
        
        # Platform Details
        'platform', 'platformversion', 'interface',
        
        # Additional Metadata
        'metadata', 'notation', 'starttime', 'endtime', 'timezone',
        
        # Game Quality Metrics
        'accuracy', 'complexity', 'evaluation', 'quality',
        
        # Broadcasting
        'broadcast', 'broadcaster', 'broadcasturl',
        
        # Competition Details
        'competition', 'competitiondate', 'competitiontype',
        
        # Additional Player Details
        'whiteteamrating', 'blackteamrating', 'whitenationality', 'blacknationality',
        
        # Game Context
        'context', 'continuation', 'prerequisite',
        
        # Technical Details
        'protocol', 'port', 'room', 'sessionid', 'gameid'
    }
    
    
    
    # Compile regex pattern once - making it case insensitive with (?i)
    header_pattern = re.compile(r'(?i)\[(\w+)\s+"(.+)"\]')
    
    games = []
    game_data = {}
    
    for line in file_content.splitlines():
        line = convert_to_english_chars(line.strip())  # Convert special characters
        if not line:
            continue
            
        if line.startswith('['):
            # Case insensitive check for new game
            if re.match(r'(?i)\[event\s+', line) and game_data:
                games.append(game_data)
                game_data = {}
            
            match = header_pattern.match(line)
            if match:
                key, value = match.groups()
                # Convert key to lowercase for consistent comparison
                key_lower = key.lower()
                # Store original key to preserve case in output
                if key_lower in PRESERVE_LINE_KEYS:
                    game_data[key] = line.replace(',', ' ')
                else:
                    game_data[key] = value
        elif line:
            game_data.setdefault('Moves', []).append(line)
    
    if game_data:
        games.append(game_data)
    
    return games







def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9 ]', '', filename).strip()

def replace_double_spaces(filename):
    return re.sub(r'\s{2,}', ' ', filename)

def check_and_correct_filepath(filepath):
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)



def write_game_to_file(filepath: str, game: Dict[str, str]) -> None:
    """Write game data to PGN file with optimized I/O."""
    lines = []
    for key, value in game.items():
        if key != 'Moves':
            if key in ('White', 'Black'):
                lines.append(f'[{key} "{value}"]')
            else:
                lines.append(str(value))
    
    lines.extend(['', '\n'.join(game.get('Moves', [])), ''])
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))



def save_game(game, players_mode, openings_mode, eco_mode, eco_list):
    output_dir = 'output'
    
    # Clean up White and Black values by removing extra "]" characters and spaces between name and initial
    if 'White' in game:
        white_value = game['White']
        if white_value.endswith('"]"]'):
            game['White'] = white_value[:-1]
        # Remove extra spaces between name and initial
        game['White'] = re.sub(r'\s+([A-Z]\.]?")', r' \1', game['White'])
    
    if 'Black' in game:
        black_value = game['Black']
        if black_value.endswith('"]"]'):
            game['Black'] = black_value[:-1]
        # Remove extra spaces between name and initial
        game['Black'] = re.sub(r'\s+([A-Z]\.]?")', r' \1', game['Black'])

    # Clean up White and Black values to remove duplicate words and brackets
    if 'White' in game:
        game['White'] = game['White'].replace('[White "', '').replace('"]', '').strip()
    if 'Black' in game:
        game['Black'] = game['Black'].replace('[Black "', '').replace('"]', '').strip()

    eco_tag = game.get('ECO')
    if eco_mode and eco_tag:
        eco_name = eco_tag.split('"')[1]
        eco_prefix = eco_name[:3]
        eco_replacement = next((line for line in eco_list if line.startswith(eco_prefix)), eco_name)
        eco_name = eco_replacement
        
        eco_name = ' '.join(eco_name.split())
        eco_dir = os.path.join(output_dir, eco_name)
        check_and_correct_filepath(eco_dir)
        
        filename = f'{replace_double_spaces(sanitize_filename(game.get("White", "Unknown")))} vs {replace_double_spaces(sanitize_filename(game.get("Black", "Unknown")))}.pgn'
        filepath = os.path.join(eco_dir, filename)
        check_and_correct_filepath(filepath)
        
        write_game_to_file(filepath, game)

    elif players_mode:
        player_w = replace_double_spaces(sanitize_filename(game.get('White', 'Unknown'))).replace('White', '')
        player_b = replace_double_spaces(sanitize_filename(game.get('Black', 'Unknown'))).replace('Black', '')
        player_dir_w = os.path.join(output_dir, player_w)
        player_dir_b = os.path.join(output_dir, player_b)
        check_and_correct_filepath(player_dir_w)
        check_and_correct_filepath(player_dir_b)
        
        filename = f'{player_w} vs {player_b}.pgn'
        filepath_w = os.path.join(player_dir_w, filename)
        filepath_b = os.path.join(player_dir_b, filename)
        
        check_and_correct_filepath(filepath_w)
        check_and_correct_filepath(filepath_b)
        
        write_game_to_file(filepath_w, game)
        write_game_to_file(filepath_b, game)

    elif openings_mode:
        opening_name = replace_double_spaces(sanitize_filename(game.get('Opening', 'Unknown')))
        if opening_name == 'Unknown':
            return
        opening_dir = os.path.join(output_dir, opening_name)
        check_and_correct_filepath(opening_dir)
        
        filename = f'{replace_double_spaces(sanitize_filename(game.get("White", "Unknown")))} vs {replace_double_spaces(sanitize_filename(game.get("Black", "Unknown")))}.pgn'
        filepath = os.path.join(opening_dir, filename)
        check_and_correct_filepath(filepath)
        
        write_game_to_file(filepath, game)

    else:
        event_name = replace_double_spaces(sanitize_filename(game.get('Event', 'Unknown'))).replace('Event', 'Event')
        date_name = replace_double_spaces(sanitize_filename(game.get('Date', 'Unknown'))).replace('Date', 'Date')
        event_dir_name = f"{event_name} {date_name}"
        event_dir = os.path.join(output_dir, event_dir_name)
        check_and_correct_filepath(event_dir)
        
        player_w = replace_double_spaces(sanitize_filename(game.get('White', 'Unknown'))).replace('White', '')
        player_b = replace_double_spaces(sanitize_filename(game.get('Black', 'Unknown'))).replace('Black', '')
        filename = f'{player_w} vs {player_b}.pgn'
        filepath = os.path.join(event_dir, filename)
        check_and_correct_filepath(filepath)
        
        write_game_to_file(filepath, game)




def write_game_to_file(filepath, game):
    with open(filepath, 'w') as f:
        for key, value in game.items():
            if key != 'Moves':
                if key in ['White', 'Black']:
                    f.write(f'[{key} "{value}"]\n')
                else:
                    f.write(f"{value}\n")
        f.write('\n')
        f.write('\n'.join(game.get('Moves', [])) + '\n')




def save_games_to_files(games, players_mode, openings_mode, eco_mode, eco_list):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    for index, game in tqdm(enumerate(games, start=1), total=len(games), desc="\033[92mProcessing games\033[0m"):
        if not game.get('Moves'):
            continue
        save_game(game, players_mode, openings_mode, eco_mode, eco_list)




import argparse
import sys
import os
import glob

def combine_pgn_files(directory):
    """Combines all PGN files in the given directory into a single file named after the folder."""
    if not os.path.exists(directory):
        return
    
    folder_name = os.path.basename(directory)
    output_file = os.path.join(directory, f"{folder_name}.pgn")
    
    # Get all .pgn files in the directory
    pgn_files = glob.glob(os.path.join(directory, "*.pgn"))
    if not pgn_files:
        return
    
    # Combine all files
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for pgn_file in pgn_files:
            if os.path.basename(pgn_file) != f"{folder_name}.pgn":  # Skip the output file if it exists
                with open(pgn_file, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read() + "\n\n")

def process_one_file(base_dir, category=None):
    """Process directories to combine PGN files based on category."""
    if category:
        # Handle specific category (players, openings, eco)
        for dir_path in glob.glob(os.path.join(base_dir, "*/")):
            combine_pgn_files(dir_path.rstrip('/'))
    else:
        # Handle event folders (default case)
        for dir_path in glob.glob(os.path.join(base_dir, "*/")):
            combine_pgn_files(dir_path.rstrip('/'))




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--players', action='store_true', help='Organize output by player names')
    parser.add_argument('--openings', action='store_true', help='Organize output by openings')
    parser.add_argument('--eco', action='store_true', help='Ignore Event header and process ECO tags')
    parser.add_argument('--onefile', action='store_true', help='Combine all PGN files in each folder into one file')
    args = parser.parse_args()
    
    clear_console()
    clear_output_directory()
    clear_console()
    pgn_files = load_pgn_files()
    all_games = []
    
    eco_list = []
    if args.eco:
        with open('ecolist.txt', 'r') as eco_file:
            eco_list = [line.strip() for line in eco_file.readlines()]
    
    for pgn_file in pgn_files:
        with open(pgn_file, 'r') as f:
            file_content = f.read()
            games = parse_pgn(file_content)
            all_games.extend(games)
            
    if not any('White' in game for game in all_games) and not any('Black' in game for game in all_games):
       print("\n\033[93mNo 'PGN' file has been found in the current directory!\033[0m\n")
       return        
            
    if args.openings and not any('Opening' in game for game in all_games):
       print("\n\033[93mNo 'Opening' header tags have been found in the file!\033[0m\n")
       return

    if args.eco and not any('ECO' in game for game in all_games):
       print("\n\033[93mNo 'ECO' header tags have been found in the file!\033[0m\n")
       return
    
    if args.players and not any('White' in game for game in all_games) and not any('Black' in game for game in all_games):
       print("\n\033[93mNo 'PGN' file has been found in the current directory!\033[0m\n")
       return
    
    save_games_to_files(all_games, args.players, args.openings, args.eco, eco_list)
    
    if args.onefile:
        combine_pgn_files(args.players, args.openings, args.eco)
    
    print('\n\033[92mall operations have been completed\033[0m\n')
    if not args.openings and not args.eco:
        print('\033[94myour new files will be found in the "output" folder\033[0m\n')

def combine_pgn_files(by_players=False, by_openings=False, by_eco=False):
    output_dir = "output"
    if not os.path.exists(output_dir):
        return

    # Determine which subdirectories to process
    if by_players:
        process_type = "players"
    elif by_openings:
        process_type = "openings"
    elif by_eco:
        process_type = "eco"
    else:
        process_type = "events"

    subdirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    
    for subdir in subdirs:
        subdir_path = os.path.join(output_dir, subdir)
        pgn_files = [f for f in os.listdir(subdir_path) if f.endswith('.pgn')]
        
        if not pgn_files:
            continue
            
        combined_content = ""
        output_file = os.path.join(subdir_path, f"{subdir}.pgn")
        
        print(f"\nProcessing {subdir}...")
        
        # Create progress bar
        with tqdm(total=len(pgn_files), desc="Combining files", unit="file") as pbar:
            for pgn_file in pgn_files:
                file_path = os.path.join(subdir_path, pgn_file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    if content:
                        combined_content += content + "\n\n"
                
                # Delete the original file
                if file_path != output_file:  # Don't delete if it's the output file
                    os.remove(file_path)
                pbar.update(1)
        
        # Write the combined content
        with open(output_file, 'w') as f:
            f.write(combined_content.strip())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
