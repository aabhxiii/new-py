import discord
from discord.ext import commands
import os
import asyncio
from transformers import pipeline
import re
import datetime
import torch

# Ensure you're using PyTorch
print(torch.__version__)

# Create the sentiment analysis pipeline with PyTorch
sentiment_pipeline = pipeline("sentiment-analysis", framework="pt")

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='+', intents=intents)

# Set up the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# In-memory storage for requests and user warnings
request_log = []
user_warnings = {}
timeout_actions = {}  # Track timeout actions by users

# List of bad words (you should expand this list)
bad_words = bad_words = [ 
    # English
    "aand", "aandu", "balatkar", "beti chod", "bhadva", "bhadve", "bhandve", 
    "bhootni ke", "bhosad", "bhosadi ke", "boobe", "chakke", "chinaal", 
    "chinki", "chod", "chodu", "chodu bhagat", "chooche", "choochi", "choot", 
    "choot ke baal", "chootia", "chootiya", "chuche", "chuchi", "chudai khanaa", 
    "chudan chudai", "chut", "chut ke baal", "chut ke dhakkan", "chut maarli", 
    "chutad", "chutadd", "chutan", "chutia", "chutiya", "gaand", "gaandfat", 
    "gaandmasti", "gaandufad", "gandu", "gashti", "gasti", "ghassa", "ghasti", 
    "harami", "haramzade", "hawas", "hawas ke pujari", "hijda", "hijra", 
    "jhant", "jhant chaatu", "jhant ke baal", "jhantu", "kamine", "kaminey", 
    "kanjar", "kutta", "kutta kamina", "kutte ki aulad", "kutte ki jat", 
    "kuttiya", "loda", "lodu", "lund", "lund choos", "lund khajoor", 
    "lundtopi", "lundure", "maa ki chut", "maal", "madar chod", "mooh mein le", 
    "mutth", "najayaz", "najayaz aulaad", "najayaz paidaish", "paki", "pataka", 
    "patakha", "raand", "randi", "saala", "saala kutta", "saali kutti", 
    "saali randi", "suar", "suar ki aulad", "tatte", "tatti", "teri maa ka bhosada", 
    "teri maa ka boba chusu", "teri maa ki chut", "tharak", "tharki", "2g1c", 
    "2 girls 1 cup", "acrotomophilia", "alabama hot pocket", "alaskan pipeline", 
    "anal", "anilingus", "anus", "apeshit", "arsehole", "ass", "asshole", 
    "assmunch", "auto erotic", "autoerotic", "babeland", "baby batter", 
    "baby juice", "ball gag", "ball gravy", "ball kicking", "ball licking", 
    "ball sack", "ball sucking", "bangbros", "bareback", "barely legal", 
    "barenaked", "bastard", "bastardo", "bastinado", "bbw", "bdsm", 
    "beaner", "beaners", "beaver cleaver", "beaver lips", "bestiality", 
    "big black", "big breasts", "big knockers", "big tits", "bimbos", 
    "birdlock", "bitch", "bitches", "black cock", "blonde action", 
    "blonde on blonde action", "blowjob", "blow job", "blow your load", 
    "blue waffle", "blumpkin", "bollocks", "bondage", "boner", "boob", 
    "boobs", "booty call", "brown showers", "brunette action", "bukkake", 
    "bulldyke", "bullet vibe", "bullshit", "bung hole", "bunghole", "busty", 
    "butt", "buttcheeks", "butthole", "camel toe", "camgirl", "camslut", 
    "camwhore", "carpet muncher", "carpetmuncher", "chocolate rosebuds", 
    "circlejerk", "cleveland steamer", "clit", "clitoris", "clover clamps", 
    "clusterfuck", "cock", "cocks", "coprolagnia", "coprophilia", 
    "cornhole", "coon", "coons", "creampie", "cum", "cumming", "cunnilingus", 
    "cunt", "darkie", "date rape", "daterape", "deep throat", "deepthroat", 
    "dendrophilia", "dick", "dildo", "dingleberry", "dingleberries", 
    "dirty pillows", "dirty sanchez", "doggie style", "doggiestyle", 
    "doggy style", "doggystyle", "dog style", "dolcett", "domination", 
    "dominatrix", "dommes", "donkey punch", "double dong", "double penetration", 
    "dp action", "dry hump", "dvda", "eat my ass", "ecchi", "ejaculation", 
    "erotic", "erotism", "escort", "eunuch", "faggot", "fecal", "felch", 
    "fellatio", "feltch", "female squirting", "femdom", "figging", 
    "fingerbang", "fingering", "fisting", "foot fetish", "footjob", 
    "frotting", "fuck", "fuck buttons", "fuckin", "fucking", "fucktards", 
    "fudge packer", "fudgepacker", "futanari", "gang bang", "gay sex", 
    "genitals", "giant cock", "girl on", "girl on top", "girls gone wild", 
    "goatcx", "goatse", "god damn", "gokkun", "golden shower", "goodpoop", 
    "goo girl", "goregasm", "grope", "group sex", "g-spot", "guro", 
    "hand job", "handjob", "hard core", "hardcore", "hentai", "homoerotic", 
    "honkey", "hooker", "hot carl", "hot chick", "how to kill", "how to murder", 
    "huge fat", "humping", "incest", "intercourse", "jack off", "jail bait", 
    "jailbait", "jelly donut", "jerk off", "jigaboo", "jiggaboo", 
    "jiggerboo", "jizz", "juggs", "kike", "kinbaku", "kinkster", "kinky", 
    "knobbing", "leather restraint", "leather straight jacket", "lemon party", 
    "lolita", "lovemaking", "make me come", "male squirting", "masturbate", 
    "menage a trois", "milf", "missionary position", "motherfucker", 
    "mound of venus", "mr hands", "muff diver", "muffdiving", "nambla", 
    "nawashi", "negro", "neonazi", "nigga", "nigger", "nig nog", 
    "nimphomania", "nipple", "nipples", "nsfw images", "nude", "nudity", 
    "nympho", "nymphomania", "octopussy", "omorashi", "one cup two girls", 
    "one guy one jar", "orgasm", "orgy", "paedophile", "paki", "panties", 
    "panty", "pedobear", "pedophile", "pegging", "penis", "phone sex", 
    "piece of shit", "pissing", "piss pig", "pisspig", "playboy", 
    "pleasure chest", "pole smoker", "ponyplay", "poof", "poon", "poontang", 
    "punany", "poop chute", "poopchute", "porn", "porno", "pornography", 
    "prince albert piercing", "pthc", "pubes", "pussy", "queaf", "queef", 
    "quim", "raghead", "raging boner", "rape", "raping", "rapist", 
    "rectum", "reverse cowgirl", "rimjob", "rimming", "rosy palm", 
    "rosy palm and her 5 sisters", "rusty trombone", "sadism", "santorum", 
    "scat", "schlong", "scissoring", "semen", "sex", "sexo", "sexy", 
    "shaved beaver", "shaved pussy", "shemale", "shibari", "shit", 
    "shitblimp", "shitty", "shota", "shrimping", "skeet", "slanteye", 
    "slut", "s&m", "smut" ,"snowballing", "sodomize", "sodomy", "spic", 
    "splooge", "splooge moose","spooge", "spread legs", "spunk", "strap on", "strapon", "strappado", 
    "strip club", "style doggy", "suck", "sucks", "suicide girls", 
    "sultry women", "swastika", "swinger", "tainted love", "taste my", 
    "tea bagging", "threesome", "throating", "tied up", "tight white", 
    "tit", "tits", "titties", "titty", "tongue in a", "topless", 
    "tosser", "towelhead", "tranny", "tribadism", "tub girl", "tubgirl", 
    "tushy", "twat", "twink", "twinkie", "two girls one cup", 
    "undressing", "upskirt", "urethra play", "urophilia", "vagina", 
    "venus mound", "vibrator", "violet wand", "vorarephilia", "voyeur", 
    "vulva", "wank", "wetback", "wet dream", "white power", "wrapping men", 
    "wrinkled starfish", "xx", "xxx", "yaoi", "yellow showers", "yiffy", 
    "zoophilia", "🖕" , "आंद", "आंडू", "बलात्कार", "बेटी चोद", "भदवा", "भदवे", "भंडवे", 
    "भूतनी के", "भोसड़", "भोसड़ी के", "बूवे", "चकके", "चिनाल", 
    "चिंकी", "चोद", "चोदू", "चोदू भगत", "चूचे", "चूची", "चूत", 
    "चूत के बाल", "चूतिया", "चूतिया", "चूचे", "चूची", "चुदाई खाना", 
    "चुदान चुदाई", "चुत", "चुत के बाल", "चुत के ढक्कन", "चुत मारली", 
    "चुतड़", "चुतड़", "चुतन", "चुतिया", "चुतिया", "गांड", "गांडफट", 
    "गांडमस्ती", "गांडूफड़", "गांडू", "गाश्ती", "गस्ती", "घस्सा", "घस्ती", 
    "हरामी", "हरामजादे", "हवस", "हवस के पुजारी", "हिजड़ा", "हिजरा", 
    "झंट", "झंट चाटू", "झंट के बाल", "झंटू", "कामीने", "कामीने", 
    "कंजड़", "कुत्ता", "कुत्ता कामिना", "कुत्ते की औलाद", "कुत्ते की जात", 
    "कुत्तियाँ", "लौड़ा", "लोडू", "लंड", "लंड चूस", "लंड खजूर", 
    "लंडटोप", "लंडूरे", "माँ की चूत", "माल", "मदर चोद", "मुँह में ले", 
    "मुत्थ", "नाजायज", "नाजायज औलाद", "नाजायज पैदाइश", "पाकी", "पटाका", 
    "पटाखा", "रांड", "रंडी", "साला", "साला कुत्ता", "साली कुत्ती",
    "साली रंडी", "सुअर", "सुअर की औलाद", "टट्टे", "टट्टी", "तेरी माँ का भोसड़ा", 
    "तेरी माँ का बूबा चूसू", "तेरी माँ की चूत", "ठरक", "ठरकी", "2g1c", 
    "2 गर्ल्स 1 कप", "अक्रोटोमाफिलिया", "अलाबामा हॉट पॉकेट", "अलास्कन पाइपलाइन", 
    "एनल", "एनलिंगस", "एनस", "एपेशिट", "आर्सहोल", "अस्स", "अस्सहोल", 
    "अस्मंच", "ऑटो एरोटिक", "ऑटोएरोटिक", "बेबेलेड", "बेबी बैटर", 
    "बेबी जूस", "बॉल गैग", "बॉल ग्रेवी", "बॉल किकिंग", "बॉल लिकिंग", 
    "बॉल सैक", "बॉल सकिंग", "बैंगब्रोस", "बेयरबैक", "बेयरली लीगल", 
    "बेयरनेकेड", "बास्टर्ड", "बास्टार्डो", "बास्टिनाडो", "बीडब्ल्यू", "बीडएसएम", 
    "बीनर", "बीनर्स", "बीवर क्लिवर", "बीवर लिप्स", "बेस्टियलिटी", 
    "बिग ब्लैक", "बिग ब्रेस्ट्स", "बिग नॉकर", "बिग tits", "बिंबोस", 
    "बर्डलॉक", "बिच", "बिचेस", "ब्लैक कॉक", "ब्लोंडे एक्शन", 
    "ब्लोंडे ऑन ब्लोंडे एक्शन", "ब्लो-जॉब", "ब्लो जॉब", "ब्लो योर लोड", 
    "ब्लू वाफल", "ब्लंपकिन", "बोलक्स", "बॉन्डेज", "बोनर", "बूब", 
    "बूब्स", "बूटी कॉल", "ब्राउन शॉवर्स", "ब्रुनट एक्शन", "बुक्काके", 
    "बुल्लीडाइक", "बुलेट वाइब", "बुलशिट", "बंग होल", "बंगहोल", "बस्टी", 
    "बट", "बटचीक", "बटहोल", "कैमल टो", "कैमगर्ल", "कैमस्लट", 
    "कैमवhore", "कार्पेट मन्चर", "कार्पेटमन्चर", "चॉकलेट रोज़बड्स", 
    "सर्कलजर्क", "क्लीवलैंड स्टीमर", "क्लिट", "क्लिटोरिस", "क्लोवर क्लैम्प्स", 
    "क्लस्टरफक", "कॉक्स", "कॉक्स", "कॉप्रोलग्निया", "कॉप्रोफिलिया", 
    "कॉर्नहोल", "कून", "कून्स", "क्रेम्पी", "कम", "कमिंग", "कुनिलिंगस", 
    "कंट", "डार्की", "डेट रेप", "डेटरेप", "डीप थ्रोट", "डीपथ्रोट", 
    "डेंड्रोफिलिया", "डिक", "डिल्डो", "डिंगलबेरी", "डिंगलबेरीज़", 
    "डर्टी पिलोस", "डर्टी सांचेज़", "डॉगी स्टाइल", "डॉग्गीस्टाइल", 
    "डॉग स्टाइल", "डोल्सेट", "डोमिनेशन", "डोमिनेट्रिक्स", "डोमेस", 
    "डोंकी पंच", "डबल डोंग", "डबल पेनेट्रेशन", "डीपी एक्शन", "ड्राई हंप", 
    "डीवीडीए", "ईट माय ऐस", "एचची", "एजाकुलेशन", "एरोटिक", "एरोटिज़म", 
    "एस्कॉर्ट", "यूनच", "फैगॉट", "फीकल", "फेल्च", "फेलाटियो", 
    "फेल्टच", "फीमेल स्क्वर्टिंग", "फेमडॉम", "फिगिंग", 
    "फिंगरबैंग", "फिंगरिंग", "फिस्टिंग", "फुट फेटिश", "फुटजॉब", 
    "फ्रोटिंग", "फक", "फक बटन", "फकइन", "फकिंग", "फकटार्ड्स", 
    "फज पैकर", "फजपैकर", "फुतानरी", "गैंग बैंग", "गे सेक्स", 
    "जेनिटाल्स", "जाइंट कॉक", "गर्ल ऑन", "गर्ल ऑन टॉप", "गर्ल्स गॉन वाइल्ड", 
    "गोटेक्स", "गोट्से", "गॉड डैम", "गोक्कुन", "गोल्डन शॉवर", "गुडपूप", 
    "गू गर्ल", "गोरगास्म", "ग्रोप", "ग्रुप सेक्स", "जी-स्पॉट", "गुुरो", 
    "हैंड जॉब", "हैंडजॉब", "हार्ड कोर", "हार्डकोर", "हेंटाई", "होमोएरोटिक", 
    "होनकी", "हूकर", "हॉट कार्ल", "हॉट चीक", "हाउ टू किल", "हाउ टू मर्डर", 
    "हूज फैट", "हम्पिंग", "इंसेस्ट", "इंटरकोर्स", "जैक ऑफ", "जेल बेट", 
    "जेलबेट", "जेली डोनट", "जर्क ऑफ", "जिगाबू", "जिगगाबू", 
    "जिगरबू", "जिज्ज", "जग्स", "किक", "किन्बाकू", "किंकस्टर", "किंकी", 
    "नॉबिंग", "लेदर रिस्ट्रेंट", "लेदर स्ट्रेट जैकेट", "लेमन पार्टी", 
    "लोलीटा", "लवमेकिंग", "मे मे कम", "मेल स्क्वर्टिंग", "मास्टरबेट", 
    "मिनाजे अ ट्रॉइस", "मिल्फ", "मिशनरी पोजीशन", "मदरफकर्स", 
    "माउंड ऑफ वीनस", "एमआर हैंड्स", "मफ डाइवर", "मफडाइविंग", "नम्ब्ला", 
    "नामशी", "नीग्रो", "नीऑनाज़ी", "निग्गा", "निग्गर", "निग नग", 
    "निंफोमेनिया", "निप्पल", "निप्पल्स", "एनएसएफडब्लू इमेज", "न्यूड", "न्यूडिटी", 
    "निंफो", "निंफोमेनिया", "आक्टोपसी", "ओमोराशी", "वन कप टू गर्ल्स", 
    "वन गाय वन जार", "ऑर्गेज़म", "ऑर्गी", "पेडोफाइल", "पाकी", "पैंटीज़", 
    "पैंटी", "पेडोबियर", "पेडोफाइल", "पेगिंग", "पेनिस", "फोन सेक्स", 
    "पीस ऑफ शिट", "पिसिंग", "पिस पिग", "पिसपिग", "प्ले बॉय", 
    "प्लेजर चेस्ट", "पोल स्मोकर", "पॉनीप्ले", "पूफ", "पून", "पूनटांग", 
    "पुनानी", "पूप चूट", "पूपचूट", "पॉर्न", "पॉर्नो", "पोर्नोग्राफी", 
    "प्रिंस अल्बर्ट पियर्सिंग", "पीटीएचसी", "प्यूब्स", "पुसी", "क्वीफ", "क्वीफ", 
    "क्विम", "रागहेड", "रैजिंग बोन्", "रेप", "रेपिंग", "रेपिस्ट", 
    "रेक्टम", "रिवर्स काउगर्ल", "रिमजॉब", "रिमिंग", "रोसी पाल्म", 
    "रोसी पाल्म और उसकी 5 बहनें", "रस्ट्री ट्रॉम्बोन", "सैडीज़म", "संतोरम", 
    "स्कैट", "श्लोंग", "सिस्सरिंग", "सीमन", "सेक्स", "सेक्सो", "सेक्सी", 
    "शेव्ड बीवर", "शेव्ड पुसी", "शेमेल", "शिबारी", "शिट", 
    "शिटब्लिंप", "शिटी", "शोटा", "श्रिंपिंग", "स्कीट", "स्लांटआई", 
    "स्लट", "एस एंड एम", "स्मट" "स्नोबॉलिंग", "सोदोमाइज", "सोदोमी", "स्पिक", "स्प्लूज", "स्प्लूज मूस", 
    "स्पूज", "स्प्रेड लेग्स", "स्पंक", "स्ट्रैप ऑन", "स्ट्रैपऑन", "स्ट्रैपाडो", 
    "स्ट्रिप क्लब", "स्टाइल डॉगी", "सक", "सक्स", "सुसाइड गर्ल्स", 
    "सल्ट्रा विमेन", "स्वस्तिक", "स्विंगर", "टेनटेड लव", "टेस्ट माय", 
    "टी बैगिंग", "थ्रीसम", "थ्रोटिंग", "टाइड अप", "टाइट व्हाइट", 
    "टिट", "टिट्स", "टिट्टीज़", "टिट्टी", "टंग इन ए", "टॉपलेस", 
    "टॉसर", "टॉवेलहेड", "ट्रैनी", "त्रिबाडिज़म", "टब गर्ल", "टबगर्ल", 
    "टुशी", "ट्वाट", "ट्विंक", "ट्विंकी", "टू गर्ल्स वन कप", 
    "अंड्रेसिंग", "अपस्कर्ट", "युरेथ्रा प्ले", "यूरोफीलिया", "वजाइना", 
    "वीनस माउंड", "वाइब्रेटर", "वायलेट वांड", "वोरेरेफीलिया", "वॉयर", 
    "वल्वा", "वैंक", "वेटबैक", "वेट ड्रीम", "व्हाइट पावर", "रैपिंग मैन", 
    "रिंकल्ड स्टारफिश", "xx", "xxx", "याॅई", "येलो शावर्स", "यिफ्फी", 
    "जूफीलिया", "🖕" ]

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Event: Handle command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Error: Missing required argument. `{error.param.name}` is required.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Error: You do not have the required permissions to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Error: Command not found. Please check the command and try again.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Error: Bad argument. Please check the command usage and try again.")
    else:
        await ctx.send(f"An unexpected error occurred: {error}")
    print(f"Error: {error}")

# Command: Responds with a greeting
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

# Command: Responds with a basic ping-pong message
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

# Command: Echoes whatever message follows '!echo'
@bot.command(name='echo')
async def echo(ctx, *, message):
    await ctx.send(message)

# Custom check for administrator permissions
def is_administrator():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# Custom check for TRole
def has_trole():
    async def predicate(ctx):
        role = discord.utils.get(ctx.guild.roles, name="TRole")
        return role in ctx.author.roles or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# Command: Provides detailed information about a member
@bot.command(name='memberinfo')
@has_trole()  # Or use @commands.has_role('TRole') if you prefer built-in check
async def memberinfo(ctx, member: discord.Member):
    embed = discord.Embed(title=f"Member Info - {member}", color=discord.Color.from_rgb(255, 255, 255))
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="Bot", value=member.bot, inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Created Account", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Status", value=member.status, inline=True)
    embed.add_field(name="Activity", value=member.activity.name if member.activity else "None", inline=True)
    
    # Fetching audit logs for the most recent ban, kick, and timeout
    ban_list = []
    async for ban_entry in ctx.guild.bans():
        if ban_entry.user == member:
            ban_list.append(ban_entry)
    if ban_list:
        embed.add_field(name="Most Recent Ban", value=ban_list[-1].reason or "No reason provided", inline=True)
    else:
        embed.add_field(name="Most Recent Ban", value="None", inline=True)
    
    kicks = []
    timeouts = []
    async for entry in ctx.guild.audit_logs(limit=100):
        if entry.action == discord.AuditLogAction.kick and entry.target == member:
            kicks.append(entry)
        if entry.action == discord.AuditLogAction.member_update and entry.target == member and entry.after.timed_out_until:
            timeouts.append(entry)
    
    if kicks:
        embed.add_field(name="Most Recent Kick", value=kicks[-1].reason or "No reason provided", inline=True)
    else:
        embed.add_field(name="Most Recent Kick", value="None", inline=True)
    
    if timeouts:
        embed.add_field(name="Most Recent Timeout", value=timeouts[-1].reason or "No reason provided", inline=True)
    else:
        embed.add_field(name="Most Recent Timeout", value="None", inline=True)
    
    await ctx.send(embed=embed)

# Command: Ban a member
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned. Reason: {reason or "No reason provided"}')
    except Exception as e:
        await ctx.send(f'Failed to ban {member.mention}. Error: {e}')

# Command: Kick a member
@bot.command(name='kick')
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked. Reason: {reason or "No reason provided"}')
    except Exception as e:
        await ctx.send(f'Failed to kick {member.mention}. Error: {e}')

# Command: Timeout a member
@bot.command(name='timeout')
@has_trole()  # Or use @commands.has_role('TRole') if you prefer built-in check
async def timeout(ctx, member: discord.Member, time: str, *, reason=None):
    role_name = "Timeout"
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if not role:
        role = await ctx.guild.create_role(name=role_name, color=discord.Color.greyple())
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, add_reactions=False, speak=False)
    
    # Convert time to minutes
    time_in_minutes = 0
    if time.endswith('h'):
        time_in_minutes = int(time[:-1]) * 60
    elif time.endswith('m'):
        time_in_minutes = int(time[:-1])
    else:
        await ctx.send("Invalid time format. Use 'h' for hours or 'm' for minutes.")
        return
    
    await member.add_roles(role, reason=reason)
    await ctx.send(f'{member.mention} has been timed out for {time_in_minutes} minutes. Reason: {reason or "No reason provided"}')
    
    await asyncio.sleep(time_in_minutes * 60)
    await member.remove_roles(role, reason="Timeout expired")
    await ctx.send(f'{member.mention}\'s timeout has expired.')

# Command: Remove timeout from a member
@bot.command(name='removetimeout')
@has_trole()  # Or use @commands.has_role('TRole') if you prefer built-in check
async def removetimeout(ctx, member: discord.Member, *, reason=None):
    role_name = "Timeout"
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if role in member.roles:
        await member.remove_roles(role, reason=reason)
        await ctx.send(f'{member.mention}\'s timeout has been removed. Reason: {reason or "No reason provided"}')
    else:
        await ctx.send(f'{member.mention} does not have a timeout role.')

# Command: Show all available commands
@bot.command(name='thelp')
async def help_command(ctx):
    embed = discord.Embed(title="Help", description="List of available commands", color=discord.Color.blue())
    embed.add_field(name="!hello", value="Responds with a greeting.", inline=False)
    embed.add_field(name="!ping", value="Responds with 'Pong!'.", inline=False)
    embed.add_field(name="!echo <message>", value="Echoes the provided message.", inline=False)
    embed.add_field(name="!memberinfo @username", value="Provides detailed information about a member. (Requires TRole or Administrator)", inline=False)
    embed.add_field(name="!ban @username <reason>", value="Bans a member with an optional reason. (Requires Administrator)", inline=False)
    embed.add_field(name="!kick @username <reason>", value="Kicks a member with an optional reason. (Requires Administrator)", inline=False)
    embed.add_field(name="!timeout @username <time> <reason>", value="Times out a member for a specified time (e.g., '30m' for 30 minutes). (Requires TRole)", inline=False)
    embed.add_field(name="!removetimeout @username <reason>", value="Removes timeout from a member. (Requires TRole)", inline=False)
    await ctx.send(embed=embed)

# Command: Request a ban for a member
@bot.command(name='reqban')
@has_trole()
async def reqban(ctx, member: discord.Member, *, reason=None):
    admin_role = discord.utils.get(ctx.guild.roles, permissions=discord.Permissions(administrator=True))
    if not admin_role:
        await ctx.send("No administrator role found.")
        return

    # Log the request
    request_log.append(f"{ctx.author.name} requested a ban on {member.name}. Reason: {reason or 'No reason provided'}")

    # Send DM to all administrators
    for admin in admin_role.members:
        try:
            await admin.send(f"{ctx.author.name} has requested a ban on {member.name}. Reason: {reason or 'No reason provided'}")
        except discord.Forbidden:
            pass

    # Ensure the category exists
    category = discord.utils.get(ctx.guild.categories, name="Req-Of-Staff")
    if not category:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            discord.utils.get(ctx.guild.roles, name="TRole"): discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(ctx.guild.roles, permissions=discord.Permissions(administrator=True)): discord.PermissionOverwrite(read_messages=True)
        }
        category = await ctx.guild.create_category("Req-Of-Staff", overwrites=overwrites)

    # Create a thread in the category
    channel = await category.create_text_channel(name=f"ban-request-{ctx.author.name}-{member.name}")
    thread = await channel.create_thread(name=f"Ban Request by {ctx.author.name}", auto_archive_duration=60)
    await thread.add_user(ctx.author)
    for admin in admin_role.members:
        await thread.add_user(admin)
    await thread.add_user(member)
    await thread.send(f"{ctx.author.name} has requested a ban on {member.mention}. Reason: {reason or 'No reason provided'}")

# Command: Request a kick for a member
@bot.command(name='reqkick')
@has_trole()
async def reqkick(ctx, member: discord.Member, *, reason=None):
    admin_role = discord.utils.get(ctx.guild.roles, permissions=discord.Permissions(administrator=True))
    if not admin_role:
        await ctx.send("No administrator role found.")
        return

    # Log the request
    request_log.append(f"{ctx.author.name} requested a kick on {member.name}. Reason: {reason or 'No reason provided'}")

    # Send DM to all administrators
    for admin in admin_role.members:
        try:
            await admin.send(f"{ctx.author.name} has requested a kick on {member.name}. Reason: {reason or 'No reason provided'}")
        except discord.Forbidden:
            pass

    # Ensure the category exists
    category = discord.utils.get(ctx.guild.categories, name="Req-Of-Staff")
    if not category:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            discord.utils.get(ctx.guild.roles, name="TRole"): discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(ctx.guild.roles, permissions=discord.Permissions(administrator=True)): discord.PermissionOverwrite(read_messages=True)
        }
        category = await ctx.guild.create_category("Req-Of-Staff", overwrites=overwrites)

    # Create a thread in the category
    channel = await category.create_text_channel(name=f"kick-request-{ctx.author.name}-{member.name}")
    thread = await channel.create_thread(name=f"Kick Request by {ctx.author.name}", auto_archive_duration=60)
    await thread.add_user(ctx.author)
    for admin in admin_role.members:
        await thread.add_user(admin)
    await thread.add_user(member)
    await thread.send(f"{ctx.author.name} has requested a kick on {member.mention}. Reason: {reason or 'No reason provided'}")

# Command: Show help for reqban and reqkick
@bot.command(name='reqban_help')
async def reqban_help(ctx):
    embed = discord.Embed(title="Request Ban/Kick Help", description="How to use the request ban/kick commands", color=discord.Color.blue())
    embed.add_field(name="+reqban @username <reason>", value="Requests a ban for the specified user. Requires TRole. Provide a reason and proof. Misuse can lead to timeout or demotion.", inline=False)
    embed.add_field(name="+reqkick @username <reason>", value="Requests a kick for the specified user. Requires TRole. Provide a reason and proof. Misuse can lead to timeout or demotion.", inline=False)
    await ctx.send(embed=embed)

# Command: Show all requests made in the past
@bot.command(name='reqlog')
@commands.check(is_administrator())
async def reqlog(ctx):
    if not request_log:
        await ctx.send("No requests have been made yet.")
    else:
        log_message = "\n".join(request_log)
        await ctx.send(f"Request Log:\n{log_message}")

# Event: Monitor messages for potential conflicts and bad words
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check for bad words
    if any(word in message.content.lower() for word in bad_words):
        await handle_bad_word(message)
    else:
        # Analyze the sentiment of the message
        result = sentiment_pipeline(message.content)[0]
        
        if result['label'] == 'NEGATIVE' and result['score'] > 0.8:
            await handle_negative_message(message)

    await bot.process_commands(message)

async def handle_bad_word(message):
    user = message.author
    if user not in user_warnings:
        user_warnings[user] = {"count": 0, "last_action": None}

    user_warnings[user]["count"] += 1
    count = user_warnings[user]["count"]

    if count == 1:
        await timeout_user(user, 2 * 60 * 60)  # 2 hours
        await user.send("Please be polite next time or a bigger timeout will be applied. If this behavior continues, a timeout will be applied.")
    elif count == 2:
        await timeout_user(user, 10 * 60 * 60)  # 10 hours
        await inform_admins(user, count)
    elif count == 3:
        await timeout_user(user, 10 * 60 * 60)  # 10 hours
        await inform_admins(user, count)
    else:
        await timeout_user(user, 10 * 60 * 60)  # 10 hours
        await inform_admins(user, count)

async def handle_negative_message(message):
    user = message.author
    if user not in user_warnings:
        user_warnings[user] = {"count": 0, "last_action": None}

    user_warnings[user]["count"] += 1
    count = user_warnings[user]["count"]

    if count == 1:
        await message.channel.send(f"{user.mention}, please be mindful of your language. Let's keep the conversation respectful.")
    elif count == 2:
        await timeout_user(user, 10 * 60 * 60)  # 10 hours
        await inform_admins(user, count)

async def timeout_user(user, duration):
    try:
        await user.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration))
        await user.send(f"You have been timed out for {duration // 3600} hours due to your recent behavior. Behave or next a bigger timeout and if again persists then kick or ban will be given")
    except discord.errors.Forbidden:
        print(f"Failed to timeout {user.name}. Missing permissions.")

async def inform_admins(user, count):
    admin_role = discord.utils.get(user.guild.roles, permissions=discord.Permissions(administrator=True))
    if admin_role:
        for admin in admin_role.members:
            try:
                await admin.send(f"{user.name} has received a warning for using bad language. Total warnings: {count}.")
            except discord.Forbidden:
                print(f"Failed to send DM to {admin.name}.")

async def handle_timeout_excessive_activity(member, TRole_id, timeout_threshold=10, timeframe_minutes=5):
    guild = member.guild
    now = discord.utils.utcnow()
    
    # Fetch audit logs for timeout actions
    audit_logs = await guild.audit_logs(action=discord.AuditLogAction.MEMBER_TIMEOUT).flatten()
    
    # Filter timeout logs for the specific member and within the timeframe
    recent_timeouts = [log for log in audit_logs if log.target == member and (now - log.created_at).total_seconds() <= timeframe_minutes * 60]
    
    if len(recent_timeouts) >= timeout_threshold:
        # Remove all roles
        roles = [role for role in member.roles if role.id != guild.default_role.id]
        await member.edit(roles=[guild.default_role])

        # Timeout the member
        await member.timeout(duration=datetime.timedelta(minutes=10), reason="Excessive timeout activity")
        
        # Notify administrators
        admins = [admin for admin in guild.members if admin.guild_permissions.administrator]
        for admin in admins:
            try:
                await admin.send(f"Alert: {member} has been timed out due to excessive timeout activity. All roles have been removed.")
            except discord.Forbidden:
                pass

        # Create a thread in a specific category
        category = discord.utils.get(guild.categories, name="Category Name")  # Update with your category name
        if category:
            thread = await category.create_text_channel(name=f"timeout-discussion-{member.id}")
            await thread.send(f"**Action Taken:**\n{member} has been timed out for exceeding the threshold of timeout actions in a short period. All roles have been removed.\n**Reason:** Excessive timeout activity\n\n**Audit Logs:**")
            for log in recent_timeouts:
                await thread.send(f"**Log:** {log}")

# Replace 'YOUR_DISCORD_BOT_TOKEN' with your actual token
bot.run('MTI4NDQxODQ4MjA5OTg1MTMwNQ.G9k16g.VkMGFIjTPdeJ6oPPzo4-AYU1FVqOyYyVxOmbxY')
