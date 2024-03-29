CREATE DATABASE compsdb;
USE compsdb;

CREATE TABLE Teams (
	team_id SMALLINT AUTO_INCREMENT,
    team_name VARCHAR(50) NOT NULL UNIQUE,
    team_shortname VARCHAR(6) UNIQUE,
    team_region VARCHAR(4) NOT NULL,
    PRIMARY KEY(team_id)
);

CREATE TABLE Players (
	player_id SMALLINT AUTO_INCREMENT,
    player_ign VARCHAR(20) NOT NULL UNIQUE,
    player_role VARCHAR(20) NOT NULL,
    team_id SMALLINT NOT NULL,
    PRIMARY KEY(player_id),
    CONSTRAINT FK_player_team FOREIGN KEY (team_id)
    REFERENCES Teams(team_id)
);

CREATE TABLE Accounts (
	account_puuid CHAR(78),
    account_region VARCHAR(4) NOT NULL,
    player_id SMALLINT NOT NULL,
    PRIMARY KEY(account_puuid),
    CONSTRAINT FK_account_player FOREIGN KEY (player_id)
    REFERENCES Players(player_id)
);

CREATE TABLE Matches (
	match_id VARCHAR(16),
    match_patch VARCHAR(14) NOT NULL,
    match_timeline JSON NOT NULL,
    PRIMARY KEY (match_id)
);

CREATE TABLE MatchPicks (
	match_id VARCHAR(16),
    account_puuid CHAR(78),
    champ_id SMALLINT NOT NULL,
    player_position VARCHAR(7) NOT NULL,
    PRIMARY KEY (match_id, account_puuid),
    CONSTRAINT FK_pick_match FOREIGN KEY (match_id)
    REFERENCES Matches(match_id)
);

CREATE TABLE MatchRunes (
	match_id VARCHAR(16),
    account_puuid CHAR(78),
    rune_primary_style SMALLINT NOT NULL,
    rune_primary_1 SMALLINT NOT NULL,
    rune_primary_2 SMALLINT NOT NULL,
    rune_primary_3 SMALLINT NOT NULL,
    rune_primary_4 SMALLINT NOT NULL,
    rune_secondary_style SMALLINT NOT NULL,
    rune_secondary_1 SMALLINT NOT NULL,
    rune_secondary_2 SMALLINT NOT NULL,
    rune_stat_offense SMALLINT NOT NULL,
    rune_stat_flex SMALLINT NOT NULL,
    rune_stat_defense SMALLINT NOT NULL,
    summoner_1 SMALLINT NOT NULL,
    summoner_2 SMALLINT NOT NULL,
    PRIMARY KEY (match_id, account_puuid),
    CONSTRAINT FK_build_match FOREIGN KEY (match_id)
    REFERENCES Matches(match_id),
    CONSTRAINT FK_build_account FOREIGN KEY (account_puuid)
    REFERENCES Accounts(account_puuid)
);

CREATE TABLE MatchItems (
	match_id VARCHAR(16),
    account_puuid CHAR(78),
    item_no TINYINT,
    item_id SMALLINT NOT NULL,
    PRIMARY KEY (match_id, account_puuid, item_no),
    CONSTRAINT FK_item_match FOREIGN KEY (match_id)
    REFERENCES Matches(match_id),
    CONSTRAINT FK_item_account FOREIGN KEY (account_puuid)
    REFERENCES Accounts(account_puuid)
);

DROP TABLE MatchStats;
CREATE TABLE MatchStats (
	match_id VARCHAR(16),
    account_puuid CHAR(78),
    total_champ_damage MEDIUMINT NOT NULL,
    total_champ_shield MEDIUMINT NOT NULL,
    total_champ_heal MEDIUMINT NOT NULL,	
    total_cs SMALLINT NOT NULL,
    total_kills TINYINT NOT NULL,
    total_deaths TINYINT NOT NULL,
    total_assists TINYINT NOT NULL,
    win TINYINT NOT NULL,
    PRIMARY KEY (match_id, account_puuid),
    CONSTRAINT FK_stat_match FOREIGN KEY (match_id)
    REFERENCES Matches(match_id),
    CONSTRAINT FK_stat_account FOREIGN KEY (account_puuid)
    REFERENCES Accounts(account_puuid)
);
