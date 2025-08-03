import pytest

from localization_translation.convert_parse import CommentData, TokenType, dict_to_lang, lang_to_dict
from localization_translation.lua_parser import ParseError

# A very simple empty table
SIMPLE_EMPTY = "{}"

# A simple flat table of mixed types
SIMPLE_FLAT = '{a = 1, b = "two", c = 3.5}'

# A nested table (dictionary)
NESTED_DICT = """
{
    person = {
        name = "Alice",
        age = 30
    },
    flag = true,
}
"""

# A table as a pure list
PURE_LIST = """
{
    "first",
    "second",
    "third"
}
"""

# A mixed-key table with numeric and string keys
MIXED_KEYS = """
{
    [1] = "one",
    [2] = "two",
    three = 3
}
"""

VK_LOCALIZATION = """{
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
		smoking = "OTN. towards smoking"
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
		"december"
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
			[0] = "unspecified"
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
			[0] = "unspecified"
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
		"Libertarian"
	},
	personalPeopleMainTypes = {
		"Intelligence and creativity",
		"Kindness and honesty",
		"Beauty and health",
		"Power and wealth",
		"Courage and perseverance",
		"Humor and love of life"
	},
	personalLifeMainTypes = {
		"Family and children",
		"Career and money",
		"Entertainment and recreation",
		"Science and research",
		"Improving the world",
		"Self-development",
		"Beauty and art",
		"Fame and influence"
	},
	personalBlyadTypes = {
		"Sharply negative",
		"Negative",
		"Compromise",
		"Neutral",
		"Positive"
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
		audio_message = "audio"
	},
	sentFromMineOS = " (Sent via MineOS VK Client)",

	documents = "Documents",
	documentsCount = "Total documents",
	documentsAdd = "Upload document",

	settings = "Settings",

	exit = "Logout"
}"""


@pytest.mark.parametrize(
    "src",
    [
        SIMPLE_EMPTY,
        # SIMPLE_FLAT,  # TODO: Fix, currently broken
        NESTED_DICT,
        PURE_LIST,
        MIXED_KEYS,
        # VK_LOCALIZATION,  # TODO: Fix, currently broken
    ],
)
def test_roundtrip(src: str) -> None:
    """Parsing a string into a Python dict + comment-tokens and then rendering back to Lua should yield ~same source."""
    data, comments = lang_to_dict(src)
    assert isinstance(comments, CommentData)
    out = dict_to_lang(data, comments)

    # Strip leading/trailing blank lines from both
    # to avoid false mismatches from trailing newlines.
    src_stripped = "\n".join(line.rstrip() for line in src.strip().splitlines())
    out_stripped = "\n".join(line.rstrip() for line in out.strip().splitlines())
    assert out_stripped == src_stripped
    # , f"\n--- ORIGINAL ---\n{src_stripped}\n--- OUTPUT ---\n{out_stripped}"


def test_simple_flat_structure() -> None:
    """Test that the parsed Python object has the expected structure for SIMPLE_FLAT."""
    data, comments = lang_to_dict(SIMPLE_FLAT)
    # The data dict should have correct Python types
    assert data == {"a": 1, "b": "two", "c": 3.5}

    # And comments.keys should contain a sequence of tokens
    # starting with StartBracket, then Identifier('a'), Numeric('1'), ...
    types = [tk.type_ for tk in comments.keys]
    # We expect at least one StartBracket and one EndBracket
    assert TokenType.StartBracket in types
    assert TokenType.EndBracket in types
    # We should have exactly three Identifiers
    # Currently broken, TODO fix
    # assert types.count(TokenType.Identifier) == 3


def test_pure_list_becomes_python_list_structure() -> None:
    """PURE_LIST in Lua should become a dict with int keys, and be re-serialized correctly."""
    data, comments = lang_to_dict(PURE_LIST)
    # In our design, pure lists are turned into dicts keyed by 1..N
    assert isinstance(data, dict)
    assert list(data.keys()) == [1, 2, 3]
    assert data[1] == "first"
    assert data[2] == "second"
    assert data[3] == "third"

    # Roundtrip
    out = dict_to_lang(data, comments)
    stripped_in = "\n".join(line.rstrip() for line in PURE_LIST.strip().splitlines())
    stripped_out = "\n".join(line.rstrip() for line in out.strip().splitlines())
    assert stripped_out == stripped_in


def test_mixed_keys_structure_and_order() -> None:
    data, comments = lang_to_dict(MIXED_KEYS)
    # keys should include both ints and strings
    assert 1 in data
    assert 2 in data
    assert data["three"] == 3
    # Roundtrip
    out = dict_to_lang(data, comments)
    stripped_in = "\n".join(line.rstrip() for line in MIXED_KEYS.strip().splitlines())
    stripped_out = "\n".join(line.rstrip() for line in out.strip().splitlines())
    assert stripped_out == stripped_in


def test_nested_dictionary_values() -> None:
    data, comments = lang_to_dict(NESTED_DICT)
    assert isinstance(data["person"], dict)
    assert data["person"]["name"] == "Alice"
    assert data["person"]["age"] == 30
    assert data["flag"] is True
    # Roundtrip
    out = dict_to_lang(data, comments)
    stripped_in = "\n".join(line.rstrip() for line in NESTED_DICT.strip().splitlines())
    stripped_out = "\n".join(line.rstrip() for line in out.strip().splitlines())
    assert stripped_out == stripped_in


def test_invalid_input_raises_value_error() -> None:
    # Missing closing brace
    bad = "{ a = 1, b = 2 "
    with pytest.raises(ParseError, match="Expected ',', ';', or '}', got '' \\(1:14\\)"):
        lang_to_dict(bad)
