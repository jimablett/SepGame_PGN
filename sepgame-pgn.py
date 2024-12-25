import shutil
import platform
import argparse
from tqdm import tqdm
import sys
from typing import List, Dict
import glob
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor
import os
import re




def clear_console():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

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
    init()
    pgn_files = [f for f in os.listdir() if f.endswith('.pgn')]
    if not pgn_files:
        print(f"{Fore.RED}No PGN files found in the current directory.{Style.RESET_ALL}")
        return []
    total_size = sum(os.path.getsize(f) for f in pgn_files)
    print(f"{Fore.CYAN}Found {len(pgn_files)} PGN files to process{Style.RESET_ALL}")
    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"{Fore.GREEN}Loading PGN files{Style.RESET_ALL}") as pbar:
        loaded_files = []
        for file in pgn_files:
            file_size = os.path.getsize(file)
            loaded_files.append(file)
            print(f"{Fore.YELLOW}Loaded: {file}{Style.RESET_ALL}")
            pbar.update(file_size)
    print(f"{Fore.GREEN}Successfully loaded {len(loaded_files)} PGN files{Style.RESET_ALL}")
    return loaded_files

CHAR_MAP = {
    'ä':'a', 'ö':'o', 'ü':'u', 'ß':'ss', 'Ä':'A', 'Ö':'O', 'Ü':'U',
    'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n', 'Á':'A', 'É':'E',
    'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N', 'à':'a', 'â':'a', 'è':'e', 'ê':'e',
    'ë':'e', 'î':'i', 'ï':'i', 'ô':'o', 'ù':'u', 'û':'u', 'ÿ':'y', 'ç':'c',
    'À':'A', 'Â':'A', 'È':'E', 'Ê':'E', 'Ë':'E', 'Î':'I', 'Ï':'I', 'Ô':'O',
    'Ù':'U', 'Û':'U', 'Ÿ':'Y', 'Ç':'C', 'ã':'a', 'õ':'o', 'Ã':'A', 'Õ':'O'
}

def convert_to_english_chars(text: str) -> str:
    return ''.join(CHAR_MAP.get(c, c) for c in text)

PRESERVE_LINE_KEYS = {
    'event', 'eventdate', 'eventsponsor', 'eventtype', 'eventrounds', 'eventcountry',
    'eventcategory', 'site', 'date', 'time', 'utctime', 'utcdate', 'white', 'whiteelo',
    'whitetitle', 'whiteuscf', 'whitena', 'whitetype', 'whiteteam', 'whiteteamcountry',
    'whiteacpl', 'whitefideid', 'whiteratingdiff', 'whiterd', 'whiterating', 'black',
    'blackelo', 'blacktitle', 'blackuscf', 'blackna', 'blacktype', 'blackteam',
    'blackteamcountry', 'blackacpl', 'blackfideid', 'blackratingdiff', 'blackrd',
    'blackrating', 'round', 'result', 'eco', 'nic', 'opening', 'variation', 'subvariation',
    'timecontrol', 'setup', 'fen', 'termination', 'variant', 'mode', 'annotator',
    'beauty', 'plycount', 'sourcequality', 'section', 'stage', 'board', 'table',
    'source', 'sourcetitle', 'sourcedate', 'sourceversion', 'sourceversiondate',
    'clock', 'increment', 'timeseal', 'rated', 'promotion', 'whitestatus', 'blackstatus',
    'whiteactive', 'blackactive', 'tournamenttype', 'tournamentname', 'tournamentdate',
    'tournamentrounds', 'gametype', 'gamevariant', 'gamephase', 'gameresult',
    'gameduration', 'whitetime', 'blacktime', 'whiteclock', 'blackclock', 'averageelo',
    'ratingtype', 'ratingcategory', 'platform', 'platformversion', 'interface',
    'metadata', 'notation', 'starttime', 'endtime', 'timezone', 'accuracy', 'complexity',
    'evaluation', 'quality', 'broadcast', 'broadcaster', 'broadcasturl', 'competition',
    'competitiondate', 'competitiontype', 'whiteteamrating', 'blackteamrating',
    'whitenationality', 'blacknationality', 'context', 'continuation', 'prerequisite',
    'protocol', 'port', 'room', 'sessionid', 'gameid'
}

HEADER_PATTERN = re.compile(r'(?i)\[(\w+)\s+"(.+)"\]')

def parse_pgn(file_content: str) -> List[Dict]:
    games = []
    game_data = None
    moves = []
    
    for line in file_content.splitlines():
        line = convert_to_english_chars(line.strip())
        
        if not line:
            if moves and game_data:
                game_data['Moves'] = moves
                games.append(game_data)
                game_data = None
                moves = []
            continue
            
        if line.startswith('['):
            match = HEADER_PATTERN.match(line)
            if match:
                key, value = match.groups()
                key_lower = key.lower()
                
                if key_lower == 'event':
                    if game_data:
                        if moves:
                            game_data['Moves'] = moves
                        games.append(game_data)
                        moves = []
                    game_data = {}
                
                if game_data is None:
                    game_data = {}
                
                game_data[key] = line.replace(',', ' ') if key_lower in PRESERVE_LINE_KEYS else value
        elif line and game_data is not None:
            moves.append(line)
    
    if game_data:
        if moves:
            game_data['Moves'] = moves
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
    lines = []
    for key, value in game.items():
        if key != 'Moves':
            if key in ('White', 'Black'):
                lines.append(f'[{key} "{value}"]')
            else:
                lines.append(str(value))
    
    lines.extend(['', '\n'.join(game.get('Moves', [])), ''])
    
    unique_filepath = get_unique_filepath(filepath)
    with open(unique_filepath, 'w') as f:
        f.write('\n'.join(lines))

def get_unique_filepath(filepath: str) -> str:
    if not os.path.exists(filepath):
        return filepath
    
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    while True:
        new_filepath = os.path.join(directory, f"{counter}_{filename}")
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1

def get_next_available_filename(filepath):
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    
    if not os.path.exists(directory):
        return os.path.join(directory, f"0001_{filename}")
    
    existing_files = [f for f in os.listdir(directory) if f.endswith('.pgn')]
    highest_num = max((int(match.group(1)) for f in existing_files 
                      if (match := re.match(r'^(\d+)_', f))), default=0)
    
    return os.path.join(directory, f"{highest_num + 1:04d}_{filename}")

def save_game(game, players_mode, openings_mode, eco_mode, eco_list):
    output_dir = 'output'
    
    for player_key in ('White', 'Black'):
        if player_key in game:
            value = game[player_key]
            if value.endswith('"]"]'):
                value = value[:-1]
            value = re.sub(r'\s+([A-Z]\.]?")', r' \1', value)
            game[player_key] = value.replace(f'[{player_key} "', '').replace('"]', '').strip()

    if eco_mode and 'ECO' in game:
        eco_tag = game['ECO']
        eco_name = eco_tag.split('"')[1]
        eco_prefix = eco_name[:3]
        eco_replacement = next((line for line in eco_list if line.startswith(eco_prefix)), eco_name)
        eco_dir = os.path.join(output_dir, ' '.join(eco_replacement.split()))
        filename = f'{replace_double_spaces(sanitize_filename(game.get("White", "Unknown")))} vs {replace_double_spaces(sanitize_filename(game.get("Black", "Unknown")))}.pgn'
        filepath = get_next_available_filename(os.path.join(eco_dir, filename))
        check_and_correct_filepath(filepath)
        write_game_to_file(filepath, game)

    elif players_mode:
        player_w = replace_double_spaces(sanitize_filename(game.get('White', 'Unknown'))).replace('White', '')
        player_b = replace_double_spaces(sanitize_filename(game.get('Black', 'Unknown'))).replace('Black', '')
        filename = f'{player_w} vs {player_b}.pgn'
        
        for player_dir in (os.path.join(output_dir, player) for player in (player_w, player_b)):
            filepath = get_next_available_filename(os.path.join(player_dir, filename))
            check_and_correct_filepath(filepath)
            write_game_to_file(filepath, game)

    elif openings_mode:
        opening_name = replace_double_spaces(sanitize_filename(game.get('Opening', 'Unknown')))
        if opening_name != 'Unknown':
            opening_dir = os.path.join(output_dir, opening_name)
            filename = f'{replace_double_spaces(sanitize_filename(game.get("White", "Unknown")))} vs {replace_double_spaces(sanitize_filename(game.get("Black", "Unknown")))}.pgn'
            filepath = get_next_available_filename(os.path.join(opening_dir, filename))
            check_and_correct_filepath(filepath)
            write_game_to_file(filepath, game)

    else:
        event_name = replace_double_spaces(sanitize_filename(game.get('Event', 'Unknown'))).replace('Event', 'Event')
        date_name = replace_double_spaces(sanitize_filename(game.get('Date', 'Unknown'))).replace('Date', 'Date')
        event_dir = os.path.join(output_dir, f"{event_name} {date_name}")
        player_w = replace_double_spaces(sanitize_filename(game.get('White', 'Unknown'))).replace('White', '')
        player_b = replace_double_spaces(sanitize_filename(game.get('Black', 'Unknown'))).replace('Black', '')
        filename = f'{player_w} vs {player_b}.pgn'
        filepath = get_next_available_filename(os.path.join(event_dir, filename))
        check_and_correct_filepath(filepath)
        write_game_to_file(filepath, game)

def save_games_to_files(games, players_mode, openings_mode, eco_mode, eco_list):
    os.makedirs('output', exist_ok=True)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(save_game, game, players_mode, openings_mode, eco_mode, eco_list) for game in games]
        for future in tqdm(futures, desc="\033[92mProcessing games\033[0m"):
            future.result()

def process_one_file(base_dir, category=None):
    pattern = os.path.join(base_dir, "*/")
    for dir_path in glob.glob(pattern):
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
            eco_list = eco_file.read().splitlines()
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(parse_pgn, open(pgn_file, 'r').read()) for pgn_file in pgn_files]
        for future in futures:
            all_games.extend(future.result())
            
    if not any(game.get('White') for game in all_games):
       print("\n\033[93mNo 'PGN' file has been found in the current directory!\033[0m\n")
       return        
            
    if args.openings and not any(game.get('Opening') for game in all_games):
       print("\n\033[93mNo 'Opening' header tags have been found in the file!\033[0m\n")
       return

    if args.eco and not any(game.get('ECO') for game in all_games):
       print("\n\033[93mNo 'ECO' header tags have been found in the file!\033[0m\n")
       return
    
    if args.players and not any(game.get('White') for game in all_games):
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

    process_type = "players" if by_players else "openings" if by_openings else "eco" if by_eco else "events"
    subdirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    
    for subdir in subdirs:
        subdir_path = os.path.join(output_dir, subdir)
        pgn_files = [f for f in os.listdir(subdir_path) if f.endswith('.pgn')]
        
        if not pgn_files:
            continue
            
        output_file = os.path.join(subdir_path, f"{subdir}.pgn")
        print(f"\nProcessing {subdir}...")
        
        with open(output_file, 'w') as outfile:
            with tqdm(total=len(pgn_files), desc="Combining files", unit="file") as pbar:
                for pgn_file in pgn_files:
                    file_path = os.path.join(subdir_path, pgn_file)
                    if file_path != output_file:
                        with open(file_path, 'r') as infile:
                            content = infile.read()
                            if content:
                                outfile.write(content + "\n\n")
                        os.remove(file_path)
                    pbar.update(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)