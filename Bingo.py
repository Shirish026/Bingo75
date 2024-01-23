import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Initialize DataFrames for Bingo and Full House (FH) counts
dfBingo = pd.DataFrame(columns=['Turn No', 'Bingo'])
dfBingo['Turn No'] = range(1, 76, 1)
dfBingo = dfBingo.set_index('Turn No')
dfBingo = dfBingo.fillna(0)

dfFH = pd.DataFrame(columns=['Turn No', 'FH'])
dfFH['Turn No'] = range(1, 76, 1)
dfFH = dfFH.set_index('Turn No')
dfFH = dfFH.fillna(0)

# List to store information about first Bingo hits in each simulation
first_bingo_hits = []


def histogram_plot():
    # Read the CSV file into a DataFrame
    df_first_bingo_turns = pd.read_csv('first_bingo_turns.csv')

    # Create the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df_first_bingo_turns['First_Bingo_Turn'], bins=range(1, 76), edgecolor='black')
    plt.title('Distribution of First Bingo Hit per Player in Each Simulation')
    plt.xlabel('Turn Number When First Bingo Was Hit')
    plt.ylabel('Frequency of First Bingo Hit')
    plt.xticks(list(range(1, 76, 5)))  # setting x-ticks to show every 5th turn for clarity

    # Display the plot
    plt.show()


def get_bingo_ball(used_balls):
    # Get a random Bingo ball that hasn't been called
    all_balls = [i for i in range(1, 76)]
    available_balls = set(all_balls) - used_balls
    if available_balls:
        ball = random.choice(list(available_balls))
        used_balls.add(ball)
        return ball
    else:
        return None


def check_bingo(card):
    # Check if a Bingo card has a winning combination
    rows = card
    cols = [[card[j][i] for j in range(5)] for i in range(5)]
    dia = [[card[i][i] for i in range(5)], [card[i][4 - i] for i in range(5)]]
    lines = rows + cols + dia
    for line in lines:
        if all(cell == "X" for cell in line):
            return True
    return False


def generate_card(num_cards):
    # Generate a Bingo card with random numbers
    cards = []
    for _ in range(num_cards):
        card = [[i * 15 + j + 1 if not (i == 2 and j == 2) else "X" for j in range(5)] for i in range(5)]
        used_numbers = set()
        for i in range(5):
            for j in range(5):
                while True:
                    if j == 2 and i == 2:
                        # The center element is already called or crossed out.
                        card[i][j] = "X"
                        break
                    number = random.randint(i * 15 + 1, i * 15 + 15)
                    if number not in used_numbers:
                        card[i][j] = number
                        used_numbers.add(number)
                        break
        cards.append(card)
    return cards


def plot_graph(num_simulations, num_cards_per_simulation):
    # Plot the cumulative distribution of Bingo and FH hits
    local_df_bingo = dfBingo.copy()
    local_df_fh = dfFH.copy()

    bingo_data = pd.DataFrame({
        "Sum": local_df_bingo.sum(axis=1),
        "Std": np.std(local_df_bingo, axis=1)
    })
    bingo_data["CumSum"] = bingo_data['Sum'].cumsum() / num_simulations
    bingo_data["Variance_Bingo"] = np.var(local_df_bingo, axis=1)

    fh_data = pd.DataFrame({
        "Sum": local_df_fh.sum(axis=1),
        "Std": np.std(local_df_fh, axis=1)
    })
    fh_data["CumSum"] = fh_data['Sum'].cumsum() / num_simulations
    fh_data["Variance_FH"] = np.var(local_df_fh, axis=1)

    df_final = pd.DataFrame({
        "BingoSum": bingo_data["CumSum"],
        "FHSum": fh_data["CumSum"],
        "lower_limit_bingo": bingo_data["CumSum"] - (bingo_data["Std"] / np.sqrt(num_simulations)),
        "upper_limit_bingo": bingo_data["CumSum"] + (bingo_data["Std"] / np.sqrt(num_simulations)),
        "lower_limit_fh": fh_data["CumSum"] - (fh_data["Std"] / np.sqrt(num_simulations)),
        "upper_limit_fh": fh_data["CumSum"] + (fh_data["Std"] / np.sqrt(num_simulations)),
        "lower_var_bingo": bingo_data["CumSum"] - (bingo_data["Variance_Bingo"] / np.sqrt(num_simulations)),
        "upper_var_bingo": bingo_data["CumSum"] + (bingo_data["Variance_Bingo"] / np.sqrt(num_simulations)),
        "lower_var_fh": fh_data["CumSum"] - (fh_data["Variance_FH"] / np.sqrt(num_simulations)),
        "upper_var_fh": fh_data["CumSum"] + (fh_data["Variance_FH"] / np.sqrt(num_simulations)),
    })

    # Plotting logic
    plt.figure(figsize=(10, 8))
    plt.plot(df_final.index, df_final['BingoSum'], label='BingoSum')
    plt.plot(df_final.index, df_final['FHSum'], label='FHSum')
    plt.fill_between(df_final.index, df_final['lower_limit_bingo'],
                     df_final['upper_limit_bingo'], color='blue', alpha=0.2)
    plt.fill_between(df_final.index, df_final['lower_limit_fh'],
                     df_final['upper_limit_fh'], color='orange', alpha=0.2)

    plt.plot(df_final.index, df_final['lower_var_bingo'],
             linestyle='dashed', color='blue', label='Variance_Bingo_Lower', alpha=0.5)
    plt.plot(df_final.index, df_final['upper_var_bingo'],
             linestyle='dashed', color='blue', label='Variance_Bingo_Upper', alpha=0.5)
    plt.plot(df_final.index, df_final['lower_var_fh'],
             linestyle='dashed', color='orange', label='Variance_FH_Lower', alpha=0.5)
    plt.plot(df_final.index, df_final['upper_var_fh'],
             linestyle='dashed', color='orange', label='Variance_FH_Upper', alpha=0.5)

    plt.ylim(0, num_cards_per_simulation + 30)
    plt.xlabel("Turns")
    plt.ylabel("Number of Players")
    plt.legend()

    plt.show()


def play_bingo_simulation(num_cards):
    # Simulate the Bingo game for a given number of cards
    global dfBingo, dfFH, global_cards
    cards = generate_card(num_cards)
    global_cards = cards

    # Convert the cards to a DataFrame
    cards_df = pd.DataFrame({'Player': range(1, num_cards + 1), 'Bingo Cards': [card for card in cards]})

    # Store the DataFrame in a CSV file
    cards_df.to_csv('generated_cards.csv')

    used_balls = set()
    bingo_hits_per_card = []  # List to store the first Bingo hit for each card
    bingo_hit = [0] * num_cards
    full_house = [0] * num_cards
    turn = 0
    while turn < 75:
        # Generate a new Bingo ball
        ball = get_bingo_ball(used_balls)
        if ball is None:
            print("All Bingo balls have been drawn. The game is a tie.")
            break

        turn += 1

        # Update the Bingo cards with the new ball
        for card in cards:
            for i in range(5):
                for j in range(5):
                    if card[i][j] == ball:
                        card[i][j] = "X"

        # Check if any player has a winning Bingo card or full house
        for i, card in enumerate(cards):
            if not bingo_hit[i]:
                if check_bingo(card):
                    dfBingo['Bingo'][turn] += 1  # Add the turn number to the global list
                    first_bingo_hits.append({'Player': i + 1, 'First_Bingo_Turn': turn})
                    bingo_hit[i] = True

            if not full_house[i]:
                if all(cell == "X" for row in card for cell in row):
                    full_house[i] = True
                    dfFH['FH'][turn] += 1

    # Return the list of first Bingo hits for each card
    return bingo_hits_per_card


def main(num_cards_per_simulation, num_simulations):
    # Run multiple Bingo game simulations
    global dfBingo, dfFH
    for simulation in range(num_simulations):
        dfBingo = pd.concat([
            dfBingo, 
            pd.DataFrame(0, index=dfBingo.index, columns=[f'{simulation}th iteration Bingo'])], axis=1)
        dfFH = pd.concat([
            dfFH, 
            pd.DataFrame(0, index=dfFH.index, columns=[f'{simulation}th iteration FH'])], axis=1)
        play_bingo_simulation(num_cards_per_simulation)

    # Save data to a CSV file after the simulation loop
    df_first_bingo_turns = pd.DataFrame(first_bingo_hits, columns=['Player', 'First_Bingo_Turn'])
    df_first_bingo_turns.to_csv('first_bingo_turns.csv', index=False)
