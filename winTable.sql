/*
File: winTable.sql
Language: SQL
Date Created: April 1, 2024
Last Modified: April 4, 2024
Author: Grayson Olin

Count the amount of wins for each round of every match 
given a player's Steam ID from a CS Demo Manager database.
*/

SELECT
	rounds."number", rounds.winner_name,
	players."name", players.team_name, players.steam_id,
	COUNT(CASE WHEN rounds.winner_name = players.team_name THEN 1 END) AS win_count
FROM rounds
JOIN matches
ON matches.checksum = rounds.match_checksum
JOIN players
ON matches.checksum = players.match_checksum
WHERE 
	steam_id = 'XXXXXXXXXXXXXXXXX' AND
	rounds.winner_name = players.team_name
GROUP BY 
	rounds."number", rounds.winner_name,
	players."name", players.team_name, players.steam_id
ORDER BY rounds."number"