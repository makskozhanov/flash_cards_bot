# Telegram bot for creating flashcards

## Bot description
This bot was created as a pet project.
It allows you to create and learn flashcards.

## How to use
Once you have a bot running, you can create a deck.
A deck is a storage area for cards.

When a deck is created, you can add cards to it.
Cards have two sides: face and back.

You can create, delete and edit cards.

You can also choose the type of learning: all cards in the deck, only new cards (which have been shown less than 5 times) or learning by schedule.
There are also 3 ways of displaying cards: face first, back first and random order.

## Project structure
### main
This file is only used to register all the handlers for user actions.
It starts bot.

### config
This file defines configuration parameters for Redis and Postgres.
It sets environment variables from the .env file.

### exceptions
This file is used to describe custom exceptions.

### bot
#### init
This file creates an
instance of AsyncTeleBot and defines the storage of states.

#### bot_message
This file contains the messages that the bot sends the user.

### handlers
#### button_handlers
Defines functions to perform when user clicks or taps.

#### message_handlers
This document describes functions that are triggered by user input.

#### start
This file defines a handler that is triggered by the user command '/start'.
It specifies the initial launch of the bot.

### menu
#### keyboard_layouts
This document describes the keyboard layouts for each user state.

#### main_menu
This document defines the main menu.
The main menu varies for each user as they have their own decks.

### postgres
#### init
This document generates a SQLAlchemy engine using the provided parameters.

#### models
This file establishes SQLAlchemy models, which serve as representations of both PostgreSQL tables and Python objects.

#### database_actions
This file outlines actions related to decks and cards within a database, including their creation, deletion, renaming, and editing.

### redis_db
#### init
This file defines a Redis client instance.

#### cache_actions
This file defines actions with the Redis cache.

### user
#### user_ations
This file defines actions on users such as: create new user, get user from cache or database.

#### user_states

### utils
#### card_actions
This file defines the user states needed to assign handlers.

#### utils
This file is used to define help functions.




