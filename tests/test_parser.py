from __future__ import annotations

import pytest

from localization_translation import lua_parser


@pytest.mark.parametrize(
    ("constant", "expect"),
    [
        ("3.0", "Float[3.0]"),
        ("-3.0", "Float[-3.0]"),
        ("3.1416", "Float[3.1416]"),
        ("314.16e-2", "Float[3.1416]"),
        ("0.31416E1", "Float[0.31416]"),
        ("34e1", "Float[340.0]"),
        ("0x0.1E", "Float[0.1171875]"),
        ("0xA23p-4", "Float[162.1875]"),
        ("0X1.921FB54442D18P+1", "Float[3.141592653589793]"),
    ],
)
def test_parse_float_constants(constant: str, expect: str) -> None:
    tokens = list(lua_parser.tokenize(constant))
    parser = lua_parser.Parser(tokens)
    assert str(parser.parse_numeric_literal()) == expect


def test_tokenization() -> None:
    tokens = list(
        lua_parser.tokenize(
            """ a = 'also\\n123"'
 a = "also\\n123\\""
 a = '\\97lo\\10\\04923"'
 c = 0X1.921FB54442D18P+1
 j = 314.16e-2
 e = 0xBEBADA
 a = { [f(1)] = g; "x", "y"; x = 1, f(x), [30] = 23; 45 }""",
        ),
    )

    parser = lua_parser.Parser(tokens)
    assert str(parser.parse_identifier()) == ("Assignment[Identifier['a'], String['also\\n123\"']]")
    assert str(parser.parse_identifier()) == ("Assignment[Identifier['a'], String['also\\n123\"']]")
    assert str(parser.parse_identifier()) == ("Assignment[Identifier['a'], String['97lo1004923\"']]")
    assert str(parser.parse_identifier()) == ("Assignment[Identifier['c'], Float[3.141592653589793]]")
    assert str(parser.parse_identifier()) == ("Assignment[Identifier['j'], Float[3.1416]]")
    assert str(parser.parse_identifier()) == ("Assignment[Identifier['e'], Integer[12499674]]")
    assert str(parser.parse_identifier()) == (
        "Assignment[Identifier['a'], Table[Field[FunctionCall[Identifier['f'], Arguments[Integer[1]]], Identifier['g']], Field[Integer[1], String['x']], Field[Integer[2], String['y']], Assignment[Identifier['x'], Integer[1]], FunctionCall[Identifier['f'], Arguments[Identifier['x']]], Field[Integer[30], Integer[23]], Field[Integer[3], Integer[45]]]]"
    )


def test_weather_table() -> None:
    assert (
        lua_parser.parse_lua_table(
            """{
    winds = {
        [0] = "N",
        [1] = "NE",
        [2] = "E",
        [3] = "SE",
        [4] = "S",
        [5] = "SW",
        [6] = "W",
        [7] = "NW",
        [8] = "N",
    },
    mmHg = " mm Hg",
    speed = " m/s, ",
    population = "Population: ",
    city = "Type city name here",
    cityError = "Wrong result. Check city name and try again."
}""",
        )
        == {
            "winds": {
                0: "N",
                1: "NE",
                2: "E",
                3: "SE",
                4: "S",
                5: "SW",
                6: "W",
                7: "NW",
                8: "N",
            },
            "mmHg": " mm Hg",
            "speed": " m/s, ",
            "population": "Population: ",
            "city": "Type city name here",
            "cityError": "Wrong result. Check city name and try again.",
        }
    )


def test_vk_table() -> None:
    assert (
        lua_parser.parse_lua_table(
            """{
    leftBarOffset = 5,

    settingsStyle = "Color scheme",
    settingsAdditional = "Additional properties",

    invalidPassword = "Invalid login or password",
    username = "E-mail or phone number",
    password = "Password",
    login = "Enter",
    twoFactorEnabled = "Use 2FA",
    twoFactor = "2FA code",
    saveLogin = "Save login information:",

    loadCountConversations = "The number of loaded dialogues",
    loadCountMessages = "Number of messages to download",
    loadCountNews = "Number of downloaded news",
    scrollSpeed = "The scroll speed",
    loadCountWall = "Number of posts to download",
    loadCountFriends = "Number of friends to download",
    loadCountDocs = "Number of documents to download",

    profile = "Profile",
    message = "Message",
    sendMessage = "Send message",
    addToFriends = "Add as friend",
    friendRequestSent = "Request has been sent",
    userSubscribedToYou = "Subscribed to you",
    userIsYourFriend = "You have friends",

    profileCounters = {
        { field = "followers", description = " followers" },
        { field = "friends", description = " friends" },
        { field = "photos", description = " photos" },
        { field = "videos", description = " videos" },
        { field = "audios", description = " audio" },
    },
    profileShowAdditional = "Show details",
    profileHideAdditional = "Hide detailed information",
    profileTitleMainInformation = "Basic information",
    profileTitlePersonal = "Life position",
    profileTitleAdditions = "Personal information",
    profileTitleContacts = "Contacts",
    profileKeys = {
        education = "Education",
        inspiredBy = "Inspire",
        relation = "Relations",
        birthday = "Birthday",
        city = "City",
        homeCity = "Hometown",
        languages = "Languages",
        occupation = "Place of work",
        mobilePhone = "Mobile",
        homePhone = "Alt. phone",
        site = "Website",
        activities = "Activity",
        interests = "Interests",
        music = "Favorite music",
        movies = "Favorite movie",
        books = "Favorite book",
        tv = "Favorite show",
        games = "Favorite game",
        quotes = "Favorite quote",
        religion = "Outlook",
        political = "Polit. conviction",
        peopleMain = "People most important",
        lifeMain = "Life most important",
        alcohol = "OTN. for alcohol",
        smoking = "OTN. towards smoking",
    },
    months = {
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    },
    relationStatuses = {
        {
            "not married",
            "have a girlfriend",
            "engaged",
            "married",
            "it's complicated",
            "in active search",
            "lover",
            "in civil marriage",
            [0] = "unspecified",
        },
        {
            "not married",
            "have a friend",
            "engaged",
            "married",
            "it's complicated",
            "in active search",
            "lover",
            "in civil marriage",
            [0] = "unspecified",
        }
    },
    personalPoliticalTypes = {
        "Communist",
        "Socialist",
        "Moderate",
        "Liberal",
        "Conservative",
        "Monarchical",
        "Ultraconservative",
        "Indifferent",
        "Libertarian",
    },
    personalPeopleMainTypes = {
        "Intelligence and creativity",
        "Kindness and honesty",
        "Beauty and health",
        "Power and wealth",
        "Courage and perseverance",
        "Humor and love of life",
    },
    personalLifeMainTypes = {
        "Family and children",
        "Career and money",
        "Entertainment and recreation",
        "Science and research",
        "Improving the world",
        "Self-development",
        "Beauty and art",
        "Fame and influence",
    },
    personalBlyadTypes = {
        "Sharply negative",
        "Negative",
        "Compromise",
        "Neutral",
        "Positive",
    },

    friends = "Friends",
    friendsOnline = "Online friends",
    friendsMutual = "Mutual friends",

    news = "Newsfeed",

    send = "Send",
    conversations = "Conversations",
    you = "You: ",
    typeMessageHere = "Write a message...",
    fwdMessages = "Information: ",
    attachments = "Investments: ",
    attachmentsTypes = {
        photo = "photo",
        video = "video",
        audio = "audio",
        doc = "document",
        link = "link",
        market = "goods",
        market_album = "product catalog",
        wall = "record",
        wall_reply = "repost",
        sticker = "sticker",
        gift = "gift",
        audio_message = "audio",
    },
    sentFromMineOS = " (Sent via MineOS VK Client)",

    documents = "Documents",
    documentsCount = "Total documents",
    documentsAdd = "Upload document",

    settings = "Settings",

    exit = "Logout",
}""",
        )
        == {
            "leftBarOffset": 5,
            "settingsStyle": "Color scheme",
            "settingsAdditional": "Additional properties",
            "invalidPassword": "Invalid login or password",
            "username": "E-mail or phone number",
            "password": "Password",
            "login": "Enter",
            "twoFactorEnabled": "Use 2FA",
            "twoFactor": "2FA code",
            "saveLogin": "Save login information:",
            "loadCountConversations": "The number of loaded dialogues",
            "loadCountMessages": "Number of messages to download",
            "loadCountNews": "Number of downloaded news",
            "scrollSpeed": "The scroll speed",
            "loadCountWall": "Number of posts to download",
            "loadCountFriends": "Number of friends to download",
            "loadCountDocs": "Number of documents to download",
            "profile": "Profile",
            "message": "Message",
            "sendMessage": "Send message",
            "addToFriends": "Add as friend",
            "friendRequestSent": "Request has been sent",
            "userSubscribedToYou": "Subscribed to you",
            "userIsYourFriend": "You have friends",
            "profileCounters": [
                {"field": "followers", "description": " followers"},
                {"field": "friends", "description": " friends"},
                {"field": "photos", "description": " photos"},
                {"field": "videos", "description": " videos"},
                {"field": "audios", "description": " audio"},
            ],
            "profileShowAdditional": "Show details",
            "profileHideAdditional": "Hide detailed information",
            "profileTitleMainInformation": "Basic information",
            "profileTitlePersonal": "Life position",
            "profileTitleAdditions": "Personal information",
            "profileTitleContacts": "Contacts",
            "profileKeys": {
                "education": "Education",
                "inspiredBy": "Inspire",
                "relation": "Relations",
                "birthday": "Birthday",
                "city": "City",
                "homeCity": "Hometown",
                "languages": "Languages",
                "occupation": "Place of work",
                "mobilePhone": "Mobile",
                "homePhone": "Alt. phone",
                "site": "Website",
                "activities": "Activity",
                "interests": "Interests",
                "music": "Favorite music",
                "movies": "Favorite movie",
                "books": "Favorite book",
                "tv": "Favorite show",
                "games": "Favorite game",
                "quotes": "Favorite quote",
                "religion": "Outlook",
                "political": "Polit. conviction",
                "peopleMain": "People most important",
                "lifeMain": "Life most important",
                "alcohol": "OTN. for alcohol",
                "smoking": "OTN. towards smoking",
            },
            "months": [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
            ],
            "relationStatuses": [
                {
                    1: "not married",
                    2: "have a girlfriend",
                    3: "engaged",
                    4: "married",
                    5: "it's complicated",
                    6: "in active search",
                    7: "lover",
                    8: "in civil marriage",
                    0: "unspecified",
                },
                {
                    1: "not married",
                    2: "have a friend",
                    3: "engaged",
                    4: "married",
                    5: "it's complicated",
                    6: "in active search",
                    7: "lover",
                    8: "in civil marriage",
                    0: "unspecified",
                },
            ],
            "personalPoliticalTypes": [
                "Communist",
                "Socialist",
                "Moderate",
                "Liberal",
                "Conservative",
                "Monarchical",
                "Ultraconservative",
                "Indifferent",
                "Libertarian",
            ],
            "personalPeopleMainTypes": [
                "Intelligence and creativity",
                "Kindness and honesty",
                "Beauty and health",
                "Power and wealth",
                "Courage and perseverance",
                "Humor and love of life",
            ],
            "personalLifeMainTypes": [
                "Family and children",
                "Career and money",
                "Entertainment and recreation",
                "Science and research",
                "Improving the world",
                "Self-development",
                "Beauty and art",
                "Fame and influence",
            ],
            "personalBlyadTypes": [
                "Sharply negative",
                "Negative",
                "Compromise",
                "Neutral",
                "Positive",
            ],
            "friends": "Friends",
            "friendsOnline": "Online friends",
            "friendsMutual": "Mutual friends",
            "news": "Newsfeed",
            "send": "Send",
            "conversations": "Conversations",
            "you": "You: ",
            "typeMessageHere": "Write a message...",
            "fwdMessages": "Information: ",
            "attachments": "Investments: ",
            "attachmentsTypes": {
                "photo": "photo",
                "video": "video",
                "audio": "audio",
                "doc": "document",
                "link": "link",
                "market": "goods",
                "market_album": "product catalog",
                "wall": "record",
                "wall_reply": "repost",
                "sticker": "sticker",
                "gift": "gift",
                "audio_message": "audio",
            },
            "sentFromMineOS": " (Sent via MineOS VK Client)",
            "documents": "Documents",
            "documentsCount": "Total documents",
            "documentsAdd": "Upload document",
            "settings": "Settings",
            "exit": "Logout",
        }
    )
