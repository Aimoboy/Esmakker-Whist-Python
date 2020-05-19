from __future__ import annotations
from enum import IntEnum
from typing import List, cast
from random import shuffle


# Constants
player_num = 4


class CardType(IntEnum):
    Spades = 0
    Hearts = 1
    Diamonds = 2
    Clubs = 3
    Joker = 4


class Card:
    def __init__(self, num: int, card_type: CardType) -> None:
        if card_type == CardType.Joker and num != 14:
            raise Exception("A card with type Joker should have a num of 14.")

        if card_type != CardType.Joker and (num < 2 or 13 < num):
            raise Exception("A card that is not a Joker should have a num in the range [2:13]")

        self.num: int = num
        self.card_type: CardType = card_type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False

        return self.num == other.num and self.card_type == other.card_type


class Deck:
    def __init__(self) -> None:
        self.cards: List[Card] = []

    def generate_cards(self) -> None:
        for i in range(4):
            for j in range(2, 14):
                self.cards.append(Card(j, CardType(i)))

        for i in range(3):
            self.cards.append(Card(14, CardType.Joker))

    def shuffle(self) -> None:
        shuffle(self.cards)


class CallType(IntEnum):
    Pass = 0
    Nothing = 1
    Sol = 2
    RenSol = 3
    Bordlaegger = 4
    SuperBordlaegger = 5
    Vip = 6
    Gode = 7
    Halve = 8
    Sang = 9


class Call:
    def __init__(self, num: int, call_type: CallType) -> None:
        if call_type == CallType.Pass and num != 0:
            raise Exception("If the call type is Pass, then the num should be 0.")

        if call_type == CallType.Sol and num != 9:
            raise Exception("If the call type is Sol, then the num should be 9.")

        if call_type == CallType.RenSol and num != 10:
            raise Exception("If the call type is RenSol, then the num should be 10.")

        if call_type == CallType.Bordlaegger and num != 11:
            raise Exception("If the call type is Bordlaegger, then the num should be 11.")

        if call_type == CallType.SuperBordlaegger and num != 12:
            raise Exception("If the call type is SuperBordlaegger, then the num should be 12.")

        if num < 7 or 13 < num:
            raise Exception("A call that isn't a special type should have a num in the range [7:13].")

        self.num: int = num
        self.call_type: CallType = call_type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Call):
            return False

        return self.num == other.num and self.call_type == other.call_type

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Call):
            raise Exception("Compared Call with something non-Call, where the comparison isn't equality.")
        other_call: Call = cast(Call, other)

        if self.num < other_call.num:
            return True

        if int(self.call_type) < other_call.call_type:
            return True

        return False

    def __gt__(self, other: object) -> bool:
        return other < self

    def __le__(self, other: object) -> bool:
        return self < other or self == other

    def __ge__(self, other: object) -> bool:
        return other < self or self == other


class Player:
    def __init__(self) -> None:
        self.hand: List[Card] = []


class GameState(IntEnum):
    ChooseCall = 0
    ChoosePartner = 1
    ChooseTrump = 2
    Play = 3


class Game:
    def __init__(self, deck: Deck) -> None:
        self.deck: Deck = deck
        self.players: List[Player] = []

        for i in range(player_num):
            self.players.append(Player())
