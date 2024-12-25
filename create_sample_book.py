from ebooklib import epub
import os

# Create the book
book = epub.EpubBook()

# Set metadata
book.set_title("The Adventures of the Curious Cat")
book.set_language("en")
book.add_author("Anonymous")

# Create chapters
chapter1 = epub.EpubHtml(title="Chapter 1: A Leap into the Unknown",
                         file_name="chapter1.xhtml",
                         content="""<h1>Chapter 1: A Leap into the Unknown</h1>
<p>In the quaint little village of Willowbrook, nestled between rolling hills and whispering woods, lived a curious cat named Whiskers. With his sleek silver coat and piercing green eyes, Whiskers was no ordinary feline. He spent his days wandering through gardens, chasing butterflies, and pondering the mysteries of the world beyond his cozy home.</p>
<p>One sunny morning, Whiskers noticed a peculiar shimmer at the edge of the forest. The villagers often spoke of the Enchanted Glade, a place where magic lingered and strange creatures roamed. Despite countless warnings, Whiskers felt an irresistible pull to uncover its secrets.</p>
<p>As he padded softly through the tall grass, the shimmer grew brighter, enveloping him in a golden glow. Whiskers felt a strange sensation, as if he were floating, and suddenly found himself in a world unlike any he had ever imagined. Trees sparkled with crystalline leaves, rivers flowed with liquid silver, and the air hummed with an ethereal melody.</p>
<p>In this magical realm, Whiskers encountered a talking fox named Fenwick, who carried a map marked with mysterious symbols.</p>
<p>'You must be brave, traveler,' Fenwick said. 'The Glade is full of wonders, but also peril. Seek the Heartstone—it holds the key to returning home.'</p>
<p>Whiskers nodded, his green eyes alight with determination. Together, they embarked on a journey filled with puzzles, enchanting creatures, and unexpected friendships.</p>""")

chapter2 = epub.EpubHtml(title="Chapter 2: The Trials of the Glade",
                         file_name="chapter2.xhtml",
                         content="""<h1>Chapter 2: The Trials of the Glade</h1>
<p>The path to the Heartstone was fraught with challenges. First, Whiskers and Fenwick faced the Labyrinth of Light, a maze where walls shifted with every step. Guided by Fenwick's sharp wit and Whiskers' keen senses, they deciphered the glowing patterns to find their way through.</p>
<p>Next came the Bridge of Whispers, a rickety structure suspended over a chasm of swirling mist. Whispers filled the air, offering cryptic advice and riddles. Whiskers paused, his ears twitching as he solved the riddles one by one, securing their safe passage.</p>
<p>At last, they reached the Heartstone's sanctuary, guarded by a wise owl named Orla.</p>
<p>'Only those with a pure heart and a curious spirit may claim the Heartstone,' Orla hooted. She posed a final challenge: a test of character. Whiskers reflected on his journey, the courage he found within, and the friendships he forged. Orla, satisfied with his answers, revealed the Heartstone.</p>
<p>As Whiskers touched the glowing gem, a warm light enveloped him. He awoke back in Willowbrook, the shimmering forest edge now still and quiet. Though his adventure was over, the memories lingered, filling him with a newfound appreciation for the magic of curiosity and courage.</p>
<p>And so, Whiskers continued his days in Willowbrook, a little wiser, a little braver, and ever more curious about the world around him.</p>""")

# Add chapters to the book
book.add_item(chapter1)
book.add_item(chapter2)

# Define Table of Contents
book.toc = (epub.Link('chapter1.xhtml', 'Chapter 1: A Leap into the Unknown', 'chap1'),
            epub.Link('chapter2.xhtml', 'Chapter 2: The Trials of the Glade', 'chap2'))

# Add navigation files
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# Define spine
book.spine = ['nav', chapter1, chapter2]

# Write to file
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'The_Adventures_of_the_Curious_Cat.epub')

try:
    epub.write_epub(file_path, book, {})
    print(f"Book successfully created at: {file_path}")
except Exception as e:
    print(f"Error creating the book: {str(e)}")
