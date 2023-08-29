--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 10:03:02

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3508 (class 0 OID 16545)
-- Dependencies: 242
-- Data for Name: pokedex; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pokedex (pokemonid, language_id, name, description, category) FROM stdin;
MURKROW_SHADOW_FORM	9	Murkrow	Murkrow was feared and loathed as the alleged bearer of ill fortune. This Pokémon shows strong interest in anything that sparkles or glitters. It will even try to steal rings from women.	Darkness Pokémon
AERODACTYL_SHADOW_FORM	9	Aerodactyl	Aerodactyl is a Pokémon from the age of dinosaurs. It was regenerated from genetic material extracted from amber. It is imagined to have been the king of the skies in ancient times.	Fossil Pokémon
AERODACTYL_PURIFIED_FORM	9	Aerodactyl	Aerodactyl is a Pokémon from the age of dinosaurs. It was regenerated from genetic material extracted from amber. It is imagined to have been the king of the skies in ancient times.	Fossil Pokémon
ABOMASNOW	9	Abomasnow	It lives a quiet life on mountains that are perpetually covered in snow. It hides itself by whipping up blizzards.	Frost Tree Pokémon
ABOMASNOW_MEGA	9	Mega Abomasnow	It lives a quiet life on mountains that are perpetually covered in snow. It hides itself by whipping up blizzards.	Frost Tree Pokémon
ABRA	9	Abra	"Abra sleeps for 18 hours a day. However, it can sense the presence of foes even while it is sleeping. In such a situation, this Pokémon immediately teleports to safety."	Psi Pokémon
ABRA_PURIFIED_FORM	9	Abra	"Abra sleeps for 18 hours a day. However, it can sense the presence of foes even while it is sleeping. In such a situation, this Pokémon immediately teleports to safety."	Psi Pokémon
ABRA_SHADOW_FORM	9	Abra	"Abra sleeps for 18 hours a day. However, it can sense the presence of foes even while it is sleeping. In such a situation, this Pokémon immediately teleports to safety."	Psi Pokémon
ABSOL	9	Absol	"Every time Absol appears before people, it is followed by a disaster such as an earthquake or a tidal wave. As a result, it came to be known as the disaster Pokémon."	Disaster Pokémon
ABSOL_MEGA	9	Mega Absol	"Every time Absol appears before people, it is followed by a disaster such as an earthquake or a tidal wave. As a result, it came to be known as the disaster Pokémon."	Disaster Pokémon
ACCELGOR	9	Accelgor	"When its body dries out, it weakens. So, to prevent dehydration, it wraps itself in many layers of thin membrane."	Shell Out Pokémon
AERODACTYL	9	Aerodactyl	Aerodactyl is a Pokémon from the age of dinosaurs. It was regenerated from genetic material extracted from amber. It is imagined to have been the king of the skies in ancient times.	Fossil Pokémon
AERODACTYL_MEGA	9	Mega Aerodactyl	"The power of Mega Evolution has completely restored its genes. The rocks on its body are harder than diamond."	Fossil Pokémon
AGGRON	9	Aggron	Aggron claims an entire mountain as its own territory. It mercilessly beats up anything that violates its environment. This Pokémon vigilantly patrols its territory at all times.	Iron Armor Pokémon
AGGRON_MEGA	9	Mega Aggron	Aggron claims an entire mountain as its own territory. It mercilessly beats up anything that violates its environment. This Pokémon vigilantly patrols its territory at all times.	Iron Armor Pokémon
AIPOM	9	Aipom	"Aipom's tail ends in a hand-like appendage that can be cleverly manipulated. However, because the Pokémon uses its tail so much, its real hands have become rather clumsy."	Long Tail Pokémon
ALAKAZAM	9	Alakazam	"Alakazam's brain continually grows, making its head far too heavy to support with its neck. This Pokémon holds its head up using its psychokinetic power instead."	Psi Pokémon
ALAKAZAM_MEGA	9	Mega Alakazam	"It's adept at precognition. When attacks completely miss Alakazam, that's because it's seeing the future."	Psi Pokémon
ALAKAZAM_PURIFIED_FORM	9	Alakazam	"Alakazam's brain continually grows, making its head far too heavy to support with its neck. This Pokémon holds its head up using its psychokinetic power instead."	Psi Pokémon
ALAKAZAM_SHADOW_FORM	9	Alakazam	"Alakazam's brain continually grows, making its head far too heavy to support with its neck. This Pokémon holds its head up using its psychokinetic power instead."	Psi Pokémon
ALOMOMOLA	9	Alomomola	The reason it helps Pokémon in a weakened condition is that any Pokémon coming after them may also attack Alomomola.	Caring Pokémon
ALTARIA	9	Altaria	"Altaria dances and wheels through the sky among billowing, cotton-like clouds. By singing melodies in its crystal-clear voice, this Pokémon makes its listeners experience dreamy wonderment."	Humming Pokémon
ALTARIA_MEGA	9	Mega Altaria	"Altaria dances and wheels through the sky among billowing, cotton-like clouds. By singing melodies in its crystal-clear voice, this Pokémon makes its listeners experience dreamy wonderment."	Humming Pokémon
AMBIPOM	9	Ambipom	"It uses its tails for everything. If it wraps both of its tails around you and gives you a squeeze, that's proof it really likes you."	Long Tail Pokémon
AMOONGUSS	9	Amoonguss	"It lures prey close by dancing and waving its arm caps, which resemble Poké Balls, in a swaying motion."	Mushroom Pokémon
AMPHAROS	9	Ampharos	Ampharos gives off so much light that it can be seen even from space. People in the old days used the light of this Pokémon to send signals back and forth with others far away.	Light Pokémon
AMPHAROS_MEGA	9	Mega Ampharos	"Massive amounts of energy intensely stimulated Ampharos's cells, apparently awakening its long-sleeping dragon's blood."	Light Pokémon
AMPHAROS_PURIFIED_FORM	9	Ampharos	Ampharos gives off so much light that it can be seen even from space. People in the old days used the light of this Pokémon to send signals back and forth with others far away.	Light Pokémon
AMPHAROS_SHADOW_FORM	9	Ampharos	Ampharos gives off so much light that it can be seen even from space. People in the old days used the light of this Pokémon to send signals back and forth with others far away.	Light Pokémon
ANORITH	9	Anorith	Anorith was regenerated from a prehistoric fossil. This primitive Pokémon once lived in warm seas. It grips its prey firmly between its two large claws.	Old Shrimp Pokémon
ARBOK	9	Arbok	"This Pokémon is terrifically strong in order to constrict things with its body. It can even flatten steel oil drums. Once Arbok wraps its body around its foe, escaping its crushing embrace is impossible."	Cobra Pokémon
ARCANINE	9	Arcanine	"Arcanine is known for its high speed. It is said to be capable of running over 6,200 miles in a single day and night. The fire that blazes wildly within this Pokémon's body is its source of power."	Legendary Pokémon
ARCANINE_PURIFIED_FORM	9	Arcanine	"Arcanine is known for its high speed. It is said to be capable of running over 6,200 miles in a single day and night. The fire that blazes wildly within this Pokémon's body is its source of power."	Legendary Pokémon
SALAZZLE	9	Salazzle	\N	\N
STUFFUL	9	Stufful	\N	\N
ARCANINE_SHADOW_FORM	9	Arcanine	"Arcanine is known for its high speed. It is said to be capable of running over 6,200 miles in a single day and night. The fire that blazes wildly within this Pokémon's body is its source of power."	Legendary Pokémon
ARCEUS	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_BUG_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_DARK_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_DRAGON_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_ELECTRIC_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_FAIRY_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_FIGHTING_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_FIRE_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_FLYING_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_GHOST_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_GRASS_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_GROUND_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_ICE_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_POISON_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_PSYCHIC_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_ROCK_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_STEEL_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCEUS_WATER_FORM	9	Arceus	It is told in mythology that this Pokémon was born before the universe even existed.	Alpha Pokémon
ARCHEN	9	Archen	"Restored from a fossil, this ancient bird Pokémon has wings but can't yet fly."	First Bird Pokémon
ARCHEOPS	9	Archeops	"Said to be an ancestor of bird Pokémon, the muscles it uses to flap its wings are still weak, so it needs a long runway in order to take off."	First Bird Pokémon
ARIADOS	9	Ariados	Ariados's feet are tipped with tiny hooked claws that enable it to scuttle on ceilings and vertical walls. This Pokémon constricts the foe with thin and strong silk webbing.	Long Leg Pokémon
ARMALDO	9	Armaldo	Armaldo's tough armor makes all attacks bounce off. This Pokémon's two enormous claws can be freely extended or contracted. They have the power to punch right through a steel slab.	Plate Pokémon
ARON	9	Aron	"This Pokémon has a body of steel. To make its body, Aron feeds on iron ore that it digs from mountains. Occasionally, it causes major trouble by eating bridges and rails."	Iron Armor Pokémon
ARTICUNO	9	Articuno	"Articuno is a Legendary Pokémon that can control ice. The flapping of its wings chills the air. As a result, it is said that when this Pokémon flies, snow will fall."	Freeze Pokémon
ARTICUNO_PURIFIED_FORM	9	Articuno	"Articuno is a Legendary Pokémon that can control ice. The flapping of its wings chills the air. As a result, it is said that when this Pokémon flies, snow will fall."	Freeze Pokémon
ARTICUNO_SHADOW_FORM	9	Articuno	"Articuno is a Legendary Pokémon that can control ice. The flapping of its wings chills the air. As a result, it is said that when this Pokémon flies, snow will fall."	Freeze Pokémon
AUDINO	9	Audino	"It touches others with the feelers on its ears, using the sound of their heartbeats to tell how they are feeling."	Hearing Pokémon
AUDINO_MEGA	9	Mega Audino	"It touches others with the feelers on its ears, using the sound of their heartbeats to tell how they are feeling."	Hearing Pokémon
AXEW	9	Axew	"They mark their territory by leaving gashes in trees with their tusks. If a tusk breaks, a new one grows in quickly."	Tusk Pokémon
AZELF	9	Azelf	"It is thought that Uxie, Mesprit, and Azelf all came from the same egg."	Willpower Pokémon
AZUMARILL	9	Azumarill	"Azumarill's long ears are indispensable sensors. By focusing its hearing, this Pokémon can identify what kinds of prey are around, even in rough and fast-running rivers."	Aqua Rabbit Pokémon
AZURILL	9	Azurill	"Azurill spins its tail as if it were a lasso, then hurls it far. The momentum of the throw sends its body flying, too. Using this unique action, one of these Pokémon managed to hurl itself a record 33 feet."	Polka Dot Pokémon
BAGON	9	Bagon	"Bagon has a dream of one day soaring in the sky. In doomed efforts to fly, this Pokémon hurls itself off cliffs. As a result of its dives, its head has grown tough and as hard as tempered steel."	Rock Head Pokémon
BALTOY	9	Baltoy	Baltoy moves while spinning around on its one foot. Primitive wall paintings depicting this Pokémon living among people were discovered in some ancient ruins.	Clay Doll Pokémon
BANETTE	9	Banette	Banette generates energy for laying strong curses by sticking pins into its own body. This Pokémon was originally a pitiful plush doll that was thrown away.	Marionette Pokémon
BANETTE_MEGA	9	Mega Banette	\N	Marionette Pokémon
BANETTE_PURIFIED_FORM	9	Banette	Banette generates energy for laying strong curses by sticking pins into its own body. This Pokémon was originally a pitiful plush doll that was thrown away.	Marionette Pokémon
BANETTE_SHADOW_FORM	9	Banette	Banette generates energy for laying strong curses by sticking pins into its own body. This Pokémon was originally a pitiful plush doll that was thrown away.	Marionette Pokémon
BARBOACH	9	Barboach	"Barboach's sensitive whiskers serve as a superb radar system. This Pokémon hides in mud, leaving only its two whiskers exposed while it waits for prey to come along."	Whiskers Pokémon
BASCULIN_BLUE_STRIPED_FORM	9	Basculin	"When a school of Basculin appears in a lake, everything else disappears, except for Corphish and Crawdaunt. That's how violent Basculin are."	Hostile Pokémon
BASCULIN_RED_STRIPED_FORM	9	Basculin	"When a school of Basculin appears in a lake, everything else disappears, except for Corphish and Crawdaunt. That's how violent Basculin are."	Hostile Pokémon
BASTIODON	9	Bastiodon	This Pokémon is from roughly 100 million years ago. Its terrifyingly tough face is harder than steel.	Shield Pokémon
BAYLEEF	9	Bayleef	Bayleef's neck is ringed by curled-up leaves. Inside each tubular leaf is a small shoot of a tree. The fragrance of this shoot makes people peppy.	Leaf Pokémon
BEARTIC	9	Beartic	It freezes its breath to create fangs and claws of ice to fight with. Cold northern areas are its habitat.	Freezing Pokémon
BEAUTIFLY	9	Beautifly	"Beautifly's favorite food is the sweet pollen of flowers. If you want to see this Pokémon, just leave a potted flower by an open window. Beautifly is sure to come looking for pollen."	Butterfly Pokémon
BEEDRILL	9	Beedrill	"Beedrill is extremely territorial. No one should ever approach its nest—this is for their own safety. If angered, they will attack in a furious swarm."	Poison Bee Pokémon
BEEDRILL_MEGA	9	Mega Beedrill	"Its legs have become poison stingers. It stabs its prey repeatedly with the stingers on its limbs, dealing the final blow with the stinger on its rear."	Poison Bee Pokémon
BEEDRILL_PURIFIED_FORM	9	Beedrill	"Beedrill is extremely territorial. No one should ever approach its nest—this is for their own safety. If angered, they will attack in a furious swarm."	Poison Bee Pokémon
BEEDRILL_SHADOW_FORM	9	Beedrill	"Beedrill is extremely territorial. No one should ever approach its nest—this is for their own safety. If angered, they will attack in a furious swarm."	Poison Bee Pokémon
BEHEEYEM	9	Beheeyem	"It has strong psychic powers. Using its fingers that flash three different colors, it controls its opponents and rewrites their memories."	Cerebral Pokémon
BELDUM	9	Beldum	"Instead of blood, a powerful magnetic force courses throughout Beldum's body. This Pokémon communicates with others by sending controlled pulses of magnetism."	Iron Ball Pokémon
BELLOSSOM	9	Bellossom	"When Bellossom gets exposed to plenty of sunlight, the leaves ringing its body begin to spin around. This Pokémon's dancing is renowned in the southern lands."	Flower Pokémon
BELLOSSOM_PURIFIED_FORM	9	Bellossom	"When Bellossom gets exposed to plenty of sunlight, the leaves ringing its body begin to spin around. This Pokémon's dancing is renowned in the southern lands."	Flower Pokémon
BELLOSSOM_SHADOW_FORM	9	Bellossom	"When Bellossom gets exposed to plenty of sunlight, the leaves ringing its body begin to spin around. This Pokémon's dancing is renowned in the southern lands."	Flower Pokémon
BELLSPROUT	9	Bellsprout	"Bellsprout's thin and flexible body lets it bend and sway to avoid any attack, however strong it may be. From its mouth, this Pokémon spits a corrosive fluid that melts even iron."	Flower Pokémon
BELLSPROUT_PURIFIED_FORM	9	Bellsprout	"Bellsprout's thin and flexible body lets it bend and sway to avoid any attack, however strong it may be. From its mouth, this Pokémon spits a corrosive fluid that melts even iron."	Flower Pokémon
BELLSPROUT_SHADOW_FORM	9	Bellsprout	"Bellsprout's thin and flexible body lets it bend and sway to avoid any attack, however strong it may be. From its mouth, this Pokémon spits a corrosive fluid that melts even iron."	Flower Pokémon
BIBAREL	9	Bibarel	It makes its nest by damming streams with bark and mud. It is known as an industrious worker.	Beaver Pokémon
BIDOOF	9	Bidoof	It constantly gnaws on logs and rocks to whittle down its front teeth. It nests alongside water.	Plump Mouse Pokémon
BISHARP	9	Bisharp	It leads a group of Pawniard. Bisharp doesn't even change its expression when it deals the finishing blow to an opponent.	Sword Blade Pokémon
BLASTOISE	9	Blastoise	Blastoise has water spouts that protrude from its shell. The water spouts are very accurate. They can shoot bullets of water with enough accuracy to strike empty cans from a distance of over 160 feet.	Shellfish Pokémon
BLASTOISE_MEGA	9	Mega Blastoise	"The cannon on its back is as powerful as a tank gun. Its tough legs and back enable it to withstand the recoil from firing the cannon."	Shellfish Pokémon
BLASTOISE_PURIFIED_FORM	9	Blastoise	Blastoise has water spouts that protrude from its shell. The water spouts are very accurate. They can shoot bullets of water with enough accuracy to strike empty cans from a distance of over 160 feet.	Shellfish Pokémon
BLASTOISE_SHADOW_FORM	9	Blastoise	Blastoise has water spouts that protrude from its shell. The water spouts are very accurate. They can shoot bullets of water with enough accuracy to strike empty cans from a distance of over 160 feet.	Shellfish Pokémon
BLAZIKEN	9	Blaziken	"In battle, Blaziken blows out intense flames from its wrists and attacks foes courageously. The stronger the foe, the more intensely this Pokémon's wrists burn."	Blaze Pokémon
BLAZIKEN_MEGA	9	Mega Blaziken	"In battle, Blaziken blows out intense flames from its wrists and attacks foes courageously. The stronger the foe, the more intensely this Pokémon's wrists burn."	Blaze Pokémon
BLISSEY	9	Blissey	"Blissey senses sadness with its fluffy coat of fur. If it does so, this Pokémon will rush over to a sad person, no matter how far away, to share a Lucky Egg that brings a smile to any face."	Happiness Pokémon
BLITZLE	9	Blitzle	Its mane shines when it discharges electricity. They use the frequency and rhythm of these flashes to communicate.	Electrified Pokémon
BOLDORE	9	Boldore	"Its orange crystals are lumps of powerful energy. They're valuable, so Boldore is sometimes targeted for them."	Ore Pokémon
BONSLY	9	Bonsly	"If its body gets too damp, it will die. So, in a process reminiscent of sweating, its eyes expel moisture."	Bonsai Pokémon
BOUFFALANT	9	Bouffalant	"Their fluffy fur absorbs damage, even if they strike foes with a fierce headbutt."	Bash Buffalo Pokémon
BRAVIARY	9	Braviary	"Known as ""the hero of the skies,"" this Pokémon is so proud and so brave that it will never retreat, even when it's injured."	Valiant Pokémon
BRELOOM	9	Breloom	"Breloom closes in on its foe with light and sprightly footwork, then throws punches with its stretchy arms. This Pokémon's fighting technique puts boxers to shame."	Mushroom Pokémon
BRONZONG	9	Bronzong	Ancient people believed that petitioning Bronzong for rain was the way to make crops grow.	Bronze Bell Pokémon
BRONZOR	9	Bronzor	Implements shaped like it were discovered in ancient tombs. It is unknown if they are related.	Bronze Pokémon
BUDEW	9	Budew	"Over the winter, it closes its bud and endures the cold. In spring, the bud opens and releases pollen."	Bud Pokémon
BUIZEL	9	Buizel	It inflates the flotation sac around its neck and pokes its head out of the water to see what is going on.	Sea Weasel Pokémon
BULBASAUR	9	Bulbasaur	"Bulbasaur can be seen napping in bright sunlight. There is a seed on its back. By soaking up the sun's rays, the seed grows progressively larger."	Seed Pokémon
BULBASAUR_PURIFIED_FORM	9	Bulbasaur	"Bulbasaur can be seen napping in bright sunlight. There is a seed on its back. By soaking up the sun's rays, the seed grows progressively larger."	Seed Pokémon
BULBASAUR_SHADOW_FORM	9	Bulbasaur	"Bulbasaur can be seen napping in bright sunlight. There is a seed on its back. By soaking up the sun's rays, the seed grows progressively larger."	Seed Pokémon
BUNEARY	9	Buneary	The reason it keeps one ear rolled up is so it can launch a swift counterattack if it's attacked by an enemy.	Rabbit Pokémon
BURMY_PLANT_FORM	9	Burmy	"If its cloak is broken in battle, it quickly remakes the cloak with materials nearby."	Bagworm Pokémon
BURMY_SANDY_FORM	9	Burmy	"If its cloak is broken in battle, it quickly remakes the cloak with materials nearby."	Bagworm Pokémon
BURMY_TRASH_FORM	9	Burmy	"If its cloak is broken in battle, it quickly remakes the cloak with materials nearby."	Bagworm Pokémon
BUTTERFREE	9	Butterfree	"Butterfree has a superior ability to search for delicious honey from flowers. It can even search out, extract, and carry honey from flowers that are blooming over six miles from its nest."	Butterfly Pokémon
CACNEA	9	Cacnea	"Cacnea lives in arid locations such as deserts. It releases a strong aroma from its flower to attract prey. When prey comes near, this Pokémon shoots sharp thorns from its body to bring the victim down."	Cactus Pokémon
CACNEA_PURIFIED_FORM	9	Cacnea	"Cacnea lives in arid locations such as deserts. It releases a strong aroma from its flower to attract prey. When prey comes near, this Pokémon shoots sharp thorns from its body to bring the victim down."	Cactus Pokémon
CACNEA_SHADOW_FORM	9	Cacnea	"Cacnea lives in arid locations such as deserts. It releases a strong aroma from its flower to attract prey. When prey comes near, this Pokémon shoots sharp thorns from its body to bring the victim down."	Cactus Pokémon
CACTURNE	9	Cacturne	"During the daytime, Cacturne remains unmoving so that it does not lose any moisture to the harsh desert sun. This Pokémon becomes active at night when the temperature drops."	Scarecrow Pokémon
CACTURNE_PURIFIED_FORM	9	Cacturne	"During the daytime, Cacturne remains unmoving so that it does not lose any moisture to the harsh desert sun. This Pokémon becomes active at night when the temperature drops."	Scarecrow Pokémon
CACTURNE_SHADOW_FORM	9	Cacturne	"During the daytime, Cacturne remains unmoving so that it does not lose any moisture to the harsh desert sun. This Pokémon becomes active at night when the temperature drops."	Scarecrow Pokémon
CAMERUPT	9	Camerupt	"Camerupt has a volcano inside its body. Magma of 18,000 degrees Fahrenheit courses through its body. Occasionally, the humps on this Pokémon's back erupt, spewing the superheated magma."	Eruption Pokémon
CAMERUPT_MEGA	9	Mega Camerupt	"Camerupt has a volcano inside its body. Magma of 18,000 degrees Fahrenheit courses through its body. Occasionally, the humps on this Pokémon's back erupt, spewing the superheated magma."	Eruption Pokémon
CARNIVINE	9	Carnivine	It binds itself to trees in marshes. It attracts prey with its sweet-smelling drool and gulps them down.	Bug Catcher Pokémon
CARRACOSTA	9	Carracosta	"Carracosta eats every last bit of the prey it catches, even the shells and bones, to further strengthen its sturdy shell."	Prototurtle Pokémon
CARVANHA	9	Carvanha	Carvanha's strongly developed jaws and its sharply pointed fangs pack the destructive power to rip out boat hulls. Many boats have been attacked and sunk by this Pokémon.	Savage Pokémon
CASCOON	9	Cascoon	"Cascoon makes its protective cocoon by wrapping its body entirely with a fine silk from its mouth. Once the silk goes around its body, it hardens. This Pokémon prepares for its evolution inside the cocoon."	Cocoon Pokémon
CASTFORM	9	Castform	Castform's appearance changes with the weather. This Pokémon gained the ability to use the vast power of nature to protect its tiny body.	Weather Pokémon
CASTFORM_RAINY_FORM	9	Castform	Castform's appearance changes with the weather. This Pokémon gained the ability to use the vast power of nature to protect its tiny body.	Weather Pokémon
CASTFORM_SNOWY_FORM	9	Castform	Castform's appearance changes with the weather. This Pokémon gained the ability to use the vast power of nature to protect its tiny body.	Weather Pokémon
CASTFORM_SUNNY_FORM	9	Castform	Castform's appearance changes with the weather. This Pokémon gained the ability to use the vast power of nature to protect its tiny body.	Weather Pokémon
CATERPIE	9	Caterpie	"Caterpie has a voracious appetite. It can devour leaves bigger than its body right before your eyes. From its antenna, this Pokémon releases a terrifically strong odor."	Worm Pokémon
CELEBI	9	Celebi	"This Pokémon came from the future by crossing over time. It is thought that so long as Celebi appears, a bright and shining future awaits us."	Time Travel Pokémon
CHANDELURE	9	Chandelure	The spirits burned up in its ominous flame lose their way and wander this world forever.	Luring Pokémon
CHANSEY	9	Chansey	"Chansey lays nutritionally excellent eggs on an everyday basis. The eggs are so delicious, they are easily and eagerly devoured by even those people who have lost their appetite."	Egg Pokémon
CHARIZARD	9	Charizard	"Charizard flies around the sky in search of powerful opponents. It breathes fire of such great heat that it melts anything. However, it never turns its fiery breath on any opponent weaker than itself."	Flame Pokémon
CHARIZARD_MEGA_X	9	Mega Charizard X	"The overwhelming power that fills its entire body causes it to turn black and creates intense blue flames."	Flame Pokémon
CHARIZARD_MEGA_Y	9	Mega Charizard Y	"Its bond with its Trainer is the source of its power. It boasts speed and maneuverability greater than that of a jet fighter."	Flame Pokémon
CHARIZARD_PURIFIED_FORM	9	Charizard	"Charizard flies around the sky in search of powerful opponents. It breathes fire of such great heat that it melts anything. However, it never turns its fiery breath on any opponent weaker than itself."	Flame Pokémon
CHARIZARD_SHADOW_FORM	9	Charizard	"Charizard flies around the sky in search of powerful opponents. It breathes fire of such great heat that it melts anything. However, it never turns its fiery breath on any opponent weaker than itself."	Flame Pokémon
BEWEAR	9	Bewear	\N	\N
BOUNSWEET	9	Bounsweet	\N	\N
CHARMANDER	9	Charmander	"The flame that burns at the tip of its tail is an indication of its emotions. The flame wavers when Charmander is enjoying itself. If the Pokémon becomes enraged, the flame burns fiercely."	Lizard Pokémon
CHARMANDER_PURIFIED_FORM	9	Charmander	"The flame that burns at the tip of its tail is an indication of its emotions. The flame wavers when Charmander is enjoying itself. If the Pokémon becomes enraged, the flame burns fiercely."	Lizard Pokémon
CHARMANDER_SHADOW_FORM	9	Charmander	"The flame that burns at the tip of its tail is an indication of its emotions. The flame wavers when Charmander is enjoying itself. If the Pokémon becomes enraged, the flame burns fiercely."	Lizard Pokémon
CHARMELEON	9	Charmeleon	"Charmeleon mercilessly destroys its foes using its sharp claws. If it encounters a strong foe, it turns aggressive. In this excited state, the flame at the tip of its tail flares with a bluish white color."	Flame Pokémon
CHARMELEON_PURIFIED_FORM	9	Charmeleon	"Charmeleon mercilessly destroys its foes using its sharp claws. If it encounters a strong foe, it turns aggressive. In this excited state, the flame at the tip of its tail flares with a bluish white color."	Flame Pokémon
CHARMELEON_SHADOW_FORM	9	Charmeleon	"Charmeleon mercilessly destroys its foes using its sharp claws. If it encounters a strong foe, it turns aggressive. In this excited state, the flame at the tip of its tail flares with a bluish white color."	Flame Pokémon
CHATOT	9	Chatot	"It can learn and speak human words. If they gather, they all learn the same saying."	Music Note Pokémon
CHERRIM_OVERCAST_FORM	9	Cherrim	"If it senses strong sunlight, it opens its folded petals to absorb the sun's rays with its whole body."	Blossom Pokémon
CHERRIM_SUNNY_FORM	9	Cherrim	"If it senses strong sunlight, it opens its folded petals to absorb the sun's rays with its whole body."	Blossom Pokémon
CHERUBI	9	Cherubi	It evolves by sucking the energy out of the small ball where it had been storing nutrients.	Cherry Pokémon
CHIKORITA	9	Chikorita	"In battle, Chikorita waves its leaf around to keep the foe at bay. However, a sweet fragrance also wafts from the leaf, becalming the battling Pokémon and creating a cozy, friendly atmosphere all around."	Leaf Pokémon
CHIMCHAR	9	Chimchar	The gas made in its belly burns from its rear end. The fire burns weakly when it feels sick.	Chimp Pokémon
CHIMECHO	9	Chimecho	"Chimecho makes its cries echo inside its hollow body. When this Pokémon becomes enraged, its cries result in ultrasonic waves that have the power to knock foes flying."	Wind Chime Pokémon
CHINCHOU	9	Chinchou	Chinchou lets loose positive and negative electrical charges from its two antennas to make its prey faint. This Pokémon flashes its electric lights to exchange signals with others.	Angler Pokémon
CHINGLING	9	Chingling	"There is an orb inside its mouth. When it hops, the orb bounces all over and makes a ringing sound."	Bell Pokémon
CINCCINO	9	Cincinno	"The oil that seeps from its body is really smooth. For people troubled by bad skin, this oil is an effective treatment."	Scarf Pokémon
CLAMPERL	9	Clamperl	Clamperl's sturdy shell is not only good for protection—it is also used for clamping and catching prey. A fully grown Clamperl's shell will be scored with nicks and scratches all over.	Bivalve Pokémon
CLAYDOL	9	Claydol	Claydol are said to be dolls of mud made by primitive humans and brought to life by exposure to a mysterious ray. This Pokémon moves about while levitating.	Clay Doll Pokémon
CLEFABLE	9	Clefable	"Clefable moves by skipping lightly as if it were flying using its wings. Its bouncy step lets it even walk on water. It is known to take strolls on lakes on quiet, moonlit nights."	Fairy Pokémon
CLEFAIRY	9	Clefairy	"On every night of a full moon, groups of this Pokémon come out to play. When dawn arrives, the tired Clefairy return to their quiet mountain retreats and go to sleep nestled up against each other."	Fairy Pokémon
CLEFFA	9	Cleffa	"On nights with many shooting stars, Cleffa can be seen dancing in a ring. They dance through the night and stop only at the break of day, when these Pokémon quench their thirst with the morning dew."	Star Shape Pokémon
CLOYSTER	9	Cloyster	"Cloyster is capable of swimming in the sea. It does so by swallowing water, then jetting it out toward the rear. This Pokémon shoots spikes from its shell using the same system."	Bivalve Pokémon
COBALION	9	Cobalion	It has a body and heart of steel. It worked with its allies to punish people when they hurt Pokémon.	Iron Will Pokémon
COFAGRIGUS	9	Cofagrius	Grave robbers who mistake them for real coffins and get too close end up trapped inside their bodies.	Coffin Pokémon
COMBEE	9	Combee	"It collects and delivers honey to its colony. At night, they cluster to form a beehive and sleep."	Tiny Bee Pokémon
COMBUSKEN	9	Combusken	"Combusken toughens up its legs and thighs by running through fields and mountains. This Pokémon's legs possess both speed and power, enabling it to dole out 10 kicks in one second."	Young Fowl Pokémon
CONKELDURR	9	Conkeldurr	"Rather than rely on force, they master moves that utilize the centrifugal force of spinning concrete."	Muscular Pokémon
CORPHISH	9	Corphish	Corphish were originally foreign Pokémon that were imported as pets. They eventually turned up in the wild. This Pokémon is very hardy and has greatly increased its population.	Ruffian Pokémon
CORSOLA	9	Corsola	"Corsola's branches glitter very beautifully in seven colors when they catch sunlight. If any branch breaks off, this Pokémon grows it back in just one night."	Coral Pokémon
COTTONEE	9	Cottonee	"When attacked, it expels cotton from its body to create a diversion. The cotton it loses grows back in quickly."	Cotton Puff Pokémon
CRADILY	9	Cradily	Cradily roams around the ocean floor in search of food. This Pokémon freely extends its tree trunk-like neck and captures unwary prey using its eight tentacles.	Barnacle Pokémon
CRANIDOS	9	Cranidos	"Its hard skull is its distinguishing feature. It snapped trees by headbutting them, and then it fed on their ripe berries."	Head Butt Pokémon
CRAWDAUNT	9	Crawdaunt	"Crawdaunt has an extremely violent nature that compels it to challenge other living things to battle. Other life-forms refuse to live in ponds inhabited by this Pokémon, making them desolate places."	Rogue Pokémon
CRESSELIA	9	Cresselia	Those who sleep holding Cresselia's feather are assured of joyful dreams. It is said to represent the crescent moon.	Lunar Pokémon
CROAGUNK	9	Croagunk	"Inflating its poison sacs, it fills the area with an odd sound and hits flinching opponents with a poison jab."	Toxic Mouth Pokémon
STEENEE	9	Steenee	\N	\N
TSAREENA	9	Tsareena	\N	\N
CROBAT	9	Crobat	"If this Pokémon is flying by fluttering only a pair of wings on either the forelegs or hind legs, it's proof that Crobat has been flying a long distance. It switches the wings it uses if it is tired."	Bat Pokémon
CROBAT_PURIFIED_FORM	9	Crobat	"If this Pokémon is flying by fluttering only a pair of wings on either the forelegs or hind legs, it's proof that Crobat has been flying a long distance. It switches the wings it uses if it is tired."	Bat Pokémon
CROBAT_SHADOW_FORM	9	Crobat	"If this Pokémon is flying by fluttering only a pair of wings on either the forelegs or hind legs, it's proof that Crobat has been flying a long distance. It switches the wings it uses if it is tired."	Bat Pokémon
CROCONAW	9	Croconaw	"Once Croconaw has clamped its jaws on its foe, it will absolutely not let go. Because the tips of its fangs are forked back like barbed fishhooks, they become impossible to remove when they have sunk in."	Big Jaw Pokémon
CRUSTLE	9	Crustle	"Competing for territory, Crustle fight viciously. The one whose boulder is broken is the loser of the battle."	Stone Home Pokémon
CRYOGONAL	9	Cryogonal	"They are composed of ice crystals. They capture prey with chains of ice, freezing the prey at -148 degrees Fahrenheit."	Crystallizing Pokémon
CUBCHOO	9	Cubchoo	"Their snot is a barometer of health. When healthy, their snot is sticky and the power of their ice moves increases."	Chill Pokémon
CUBONE	9	Cubone	"Cubone pines for the mother it will never see again. Seeing a likeness of its mother in the full moon, it cries. The stains on the skull the Pokémon wears are made by the tears it sheds."	Lonely Pokémon
CUBONE_PURIFIED_FORM	9	Cubone	"Cubone pines for the mother it will never see again. Seeing a likeness of its mother in the full moon, it cries. The stains on the skull the Pokémon wears are made by the tears it sheds."	Lonely Pokémon
CUBONE_SHADOW_FORM	9	Cubone	"Cubone pines for the mother it will never see again. Seeing a likeness of its mother in the full moon, it cries. The stains on the skull the Pokémon wears are made by the tears it sheds."	Lonely Pokémon
CYNDAQUIL	9	Cyndaquil	"Cyndaquil protects itself by flaring up the flames on its back. The flames are vigorous if the Pokémon is angry. However, if it is tired, the flames splutter fitfully with incomplete combustion."	Fire Mouse Pokémon
DARKRAI	9	Darkrai	It can lull people to sleep and make them dream. It is active during nights of the new moon.	Pitch-Black Pokémon
DARMANITAN_STANDARD_FORM	9	Darmanitan	"Its internal fire burns at 2,500 degrees Fahrenheit, making enough power that it can destroy a dump truck with one punch."	Blazing Pokémon
DARMANITAN_STANDARD_FORM_GALARIAN_FORM	9	Darmanitan	"Its internal fire burns at 2,500 degrees Fahrenheit, making enough power that it can destroy a dump truck with one punch."	Blazing Pokémon
DARMANITAN_ZEN_FORM	9	Darmanitan	"Its internal fire burns at 2,500 degrees Fahrenheit, making enough power that it can destroy a dump truck with one punch."	Blazing Pokémon
DARMANITAN_ZEN_FORM_GALARIAN_FORM	9	Darmanitan	"Its internal fire burns at 2,500 degrees Fahrenheit, making enough power that it can destroy a dump truck with one punch."	Blazing Pokémon
DARUMAKA	9	Darumaka	"When it sleeps, it pulls its limbs into its body and its internal fire goes down to 1,100 degrees Fahrenheit."	Zen Charm Pokémon
DARUMAKA_GALARIAN_FORM	9	Darumaka	"When it sleeps, it pulls its limbs into its body and its internal fire goes down to 1,100 degrees Fahrenheit."	Zen Charm Pokémon
DEERLING_AUTUMN_FORM	9	Deerling	The turning of the seasons changes the color and scent of this Pokémon's fur. People use it to mark the seasons.	Season Pokémon
DEERLING_SPRING_FORM	9	Deerling	The turning of the seasons changes the color and scent of this Pokémon's fur. People use it to mark the seasons.	Season Pokémon
DEERLING_SUMMER_FORM	9	Deerling	The turning of the seasons changes the color and scent of this Pokémon's fur. People use it to mark the seasons.	Season Pokémon
DEERLING_WINTER_FORM	9	Deerling	The turning of the seasons changes the color and scent of this Pokémon's fur. People use it to mark the seasons.	Season Pokémon
DEINO	9	Deino	"Lacking sight, it's unaware of its surroundings, so it bumps into things and eats anything that moves."	Irate Pokémon
DELCATTY	9	Delcatty	"Delcatty prefers to live an unfettered existence in which it can do as it pleases at its own pace. Because this Pokémon eats and sleeps whenever it decides, its daily routines are completely random."	Prim Pokémon
DELIBIRD	9	Delibird	"Delibird carries its food bundled up in its tail. There once was a famous explorer who managed to reach the peak of the world's highest mountain, thanks to one of these Pokémon sharing its food."	Delivery Pokémon
DEOXYS	9	Deoxys	The DNA of a space virus underwent a sudden mutation upon exposure to a laser beam and resulted in Deoxys. The crystalline organ on this Pokémon's chest appears to be its brain.	DNA Pokémon
DEOXYS_ATTACK_FORM	9	Deoxys	The DNA of a space virus underwent a sudden mutation upon exposure to a laser beam and resulted in Deoxys. The crystalline organ on this Pokémon's chest appears to be its brain.	DNA Pokémon
DEOXYS_DEFENSE_FORM	9	Deoxys	The DNA of a space virus underwent a sudden mutation upon exposure to a laser beam and resulted in Deoxys. The crystalline organ on this Pokémon's chest appears to be its brain.	DNA Pokémon
DEOXYS_SPEED_FORM	9	Deoxys	The DNA of a space virus underwent a sudden mutation upon exposure to a laser beam and resulted in Deoxys. The crystalline organ on this Pokémon's chest appears to be its brain.	DNA Pokémon
DEWGONG	9	Dewgong	Dewgong loves to snooze on bitterly cold ice. The sight of this Pokémon sleeping on a glacier was mistakenly thought to be a mermaid by a mariner long ago.	Sea Lion Pokémon
DEWOTT	9	Dewott	"As a result of strict training, each Dewott learns different forms for using the scalchops."	Discipline Pokémon
DIALGA	9	Dialga	It has the power to control time. It appears in Sinnoh-region myths as an ancient deity.	Temporal Pokémon
DIANCIE	9	Diancie	"A sudden transformation of Carbink, its pink, glimmering body is said to be the loveliest sight in the whole world."	Jewel Pokémon
DIANCIE_MEGA	9	Mega Diancie	"A sudden transformation of Carbink, its pink, glimmering body is said to be the loveliest sight in the whole world."	Jewel Pokémon
DIGLETT	9	Diglett	"Diglett are raised in most farms. The reason is simple—wherever this Pokémon burrows, the soil is left perfectly tilled for planting crops. This soil is made ideal for growing delicious vegetables."	Mole Pokémon
GENESECT_BURN_FORM	9	Genesect	This Pokémon existed 300 million years ago. Team Plasma altered it and attached a cannon to its back.	Paleozoic Pokémon
DIGLETT_ALOLA_FORM	9	Diglett	"Diglett are raised in most farms. The reason is simple—wherever this Pokémon burrows, the soil is left perfectly tilled for planting crops. This soil is made ideal for growing delicious vegetables."	Mole Pokémon
DITTO	9	Ditto	"Ditto rearranges its cell structure to transform itself into other shapes. However, if it tries to transform itself into something by relying on its memory, this Pokémon manages to get details wrong."	Transform Pokémon
DODRIO	9	Dodrio	Watch out if Dodrio's three heads are looking in three separate directions. It's a sure sign that it is on its guard. Don't go near this Pokémon if it's being wary—it may decide to peck you.	Triple Bird Pokémon
DODUO	9	Doduo	"Doduo's two heads never sleep at the same time. Its two heads take turns sleeping, so one head can always keep watch for enemies while the other one sleeps."	Twin Bird Pokémon
DONPHAN	9	Donphan	"Donphan's favorite attack is curling its body into a ball, then charging at its foe while rolling at high speed. Once it starts rolling, this Pokémon can't stop very easily."	Armor Pokémon
DRAGONAIR	9	Dragonair	Dragonair stores an enormous amount of energy inside its body. It is said to alter weather conditions in its vicinity by discharging energy from the crystals on its neck and tail.	Dragon Pokémon
DRAGONAIR_PURIFIED_FORM	9	Dragonair	Dragonair stores an enormous amount of energy inside its body. It is said to alter weather conditions in its vicinity by discharging energy from the crystals on its neck and tail.	Dragon Pokémon
DRAGONAIR_SHADOW_FORM	9	Dragonair	Dragonair stores an enormous amount of energy inside its body. It is said to alter weather conditions in its vicinity by discharging energy from the crystals on its neck and tail.	Dragon Pokémon
DRAGONITE	9	Dragonite	Dragonite is capable of circling the globe in just 16 hours. It is a kindhearted Pokémon that leads lost and foundering ships in a storm to the safety of land.	Dragon Pokémon
DRAGONITE_PURIFIED_FORM	9	Dragonite	Dragonite is capable of circling the globe in just 16 hours. It is a kindhearted Pokémon that leads lost and foundering ships in a storm to the safety of land.	Dragon Pokémon
DRAGONITE_SHADOW_FORM	9	Dragonite	Dragonite is capable of circling the globe in just 16 hours. It is a kindhearted Pokémon that leads lost and foundering ships in a storm to the safety of land.	Dragon Pokémon
DRAPION	9	Drapion	It has the power in its clawed arms to make scrap of a car. The tips of its claws release poison.	Ogre Scorpion Pokémon
DRATINI	9	Dratini	Dratini continually molts and sloughs off its old skin. It does so because the life energy within its body steadily builds to reach uncontrollable levels.	Dragon Pokémon
DRATINI_PURIFIED_FORM	9	Dratini	Dratini continually molts and sloughs off its old skin. It does so because the life energy within its body steadily builds to reach uncontrollable levels.	Dragon Pokémon
DRATINI_SHADOW_FORM	9	Dratini	Dratini continually molts and sloughs off its old skin. It does so because the life energy within its body steadily builds to reach uncontrollable levels.	Dragon Pokémon
DRIFBLIM	9	Drifblim	"The raw material for the gas inside its body is souls. When its body starts to deflate, it's thought to carry away people and Pokémon."	Blimp Pokémon
DRIFLOON	9	Drifloon	"Wandering souls gathered together to form this Pokémon. When trying to make friends with children, Drifloon grabs them by the hand."	Balloon Pokémon
DRILBUR	9	Drilbur	"By spinning its body, it can dig straight through the ground at a speed of 30 mph."	Mole Pokémon
DROWZEE	9	Drowzee	"If your nose becomes itchy while you are sleeping, it's a sure sign that one of these Pokémon is standing above your pillow and trying to eat your dream through your nostrils."	Hypnosis Pokémon
DROWZEE_PURIFIED_FORM	9	Drowzee	"If your nose becomes itchy while you are sleeping, it's a sure sign that one of these Pokémon is standing above your pillow and trying to eat your dream through your nostrils."	Hypnosis Pokémon
DROWZEE_SHADOW_FORM	9	Drowzee	"If your nose becomes itchy while you are sleeping, it's a sure sign that one of these Pokémon is standing above your pillow and trying to eat your dream through your nostrils."	Hypnosis Pokémon
DRUDDIGON	9	Druddigon	It infiltrates tunnels that Pokémon like Diglett and Dugtrio have dug and quietly waits for prey to pass through.	Cave Pokémon
DUCKLETT	9	Ducklett	"They are better at swimming than flying, and they happily eat their favorite food, peat moss, as they dive underwater."	Water Bird Pokémon
DUGTRIO	9	Dugtrio	"Dugtrio are actually triplets that emerged from one body. As a result, each triplet thinks exactly like the other two triplets. They work cooperatively to burrow endlessly."	Mole Pokémon
DUGTRIO_ALOLA_FORM	9	Dugtrio	"Dugtrio are actually triplets that emerged from one body. As a result, each triplet thinks exactly like the other two triplets. They work cooperatively to burrow endlessly."	Mole Pokémon
DUNSPARCE	9	Dunsparce	Dunsparce has a drill for its tail. It uses this tail to burrow into the ground backward. This Pokémon is known to make its nest in complex shapes deep under the ground.	Land Snake Pokémon
DUOSION	9	Duosion	"When their two divided brains think the same thoughts, their psychic power is maximized."	Mitosis Pokémon
DURANT	9	Durant	"They attack in groups, covering themselves in steel armor to protect themselves from Heatmor."	Iron Ant Pokémon
DUSCLOPS	9	Dusclops	"Dusclops's body is completely hollow—there is nothing at all inside. It is said that its body is like a black hole. This Pokémon will absorb anything into its body, but nothing will ever come back out."	Beckon Pokémon
DUSCLOPS_PURIFIED_FORM	9	Dusclops	"Dusclops's body is completely hollow—there is nothing at all inside. It is said that its body is like a black hole. This Pokémon will absorb anything into its body, but nothing will ever come back out."	Beckon Pokémon
DUSCLOPS_SHADOW_FORM	9	Dusclops	"Dusclops's body is completely hollow—there is nothing at all inside. It is said that its body is like a black hole. This Pokémon will absorb anything into its body, but nothing will ever come back out."	Beckon Pokémon
DUSKNOIR	9	Dusknoir	The antenna on its head captures radio waves from the world of spirits that command it to take people there.	Gripper Pokémon
DUSKNOIR_PURIFIED_FORM	9	Dusknoir	The antenna on its head captures radio waves from the world of spirits that command it to take people there.	Gripper Pokémon
DUSKNOIR_SHADOW_FORM	9	Dusknoir	The antenna on its head captures radio waves from the world of spirits that command it to take people there.	Gripper Pokémon
ROTOM_WASH_FORM	9	Rotom	Its body is composed of plasma. It is known to infiltrate electronic devices and wreak havoc.	Plasma Pokémon
DUSKULL	9	Duskull	"Duskull can pass through any wall no matter how thick it may be. Once this Pokémon chooses a target, it will doggedly pursue the intended victim until the break of dawn."	Requiem Pokémon
DUSKULL_PURIFIED_FORM	9	Duskull	"Duskull can pass through any wall no matter how thick it may be. Once this Pokémon chooses a target, it will doggedly pursue the intended victim until the break of dawn."	Requiem Pokémon
DUSKULL_SHADOW_FORM	9	Duskull	"Duskull can pass through any wall no matter how thick it may be. Once this Pokémon chooses a target, it will doggedly pursue the intended victim until the break of dawn."	Requiem Pokémon
DUSTOX	9	Dustox	"Dustox is instinctively drawn to light. Swarms of this Pokémon are attracted by the bright lights of cities, where they wreak havoc by stripping the leaves off roadside trees for food."	Poison Moth Pokémon
DWEBBLE	9	Dwebble	"When it finds a stone of a suitable size, it secretes a liquid from its mouth to open up a hole to crawl into."	Rock Inn Pokémon
EELEKTRIK	9	Eelektrik	"These Pokémon have a big appetite. When they spot their prey, they attack it and paralyze it with electricity."	EleFish Pokémon
EELEKTROSS	9	Eelektross	They crawl out of the ocean using their arms. They will attack prey on shore and immediately drag it into the ocean.	EleFish Pokémon
EEVEE	9	Eevee	Eevee has an unstable genetic makeup that suddenly mutates due to the environment in which it lives. Radiation from various stones causes this Pokémon to evolve.	Evolution Pokémon
EKANS	9	Ekans	Ekans curls itself up in a spiral while it rests. Assuming this position allows it to quickly respond to a threat from any direction with a glare from its upraised head.	Snake Pokémon
ELECTABUZZ	9	Electabuzz	"When a storm arrives, gangs of this Pokémon compete with each other to scale heights that are likely to be stricken by lightning bolts. Some towns use Electabuzz in place of lightning rods."	Electric Pokémon
ELECTABUZZ_PURIFIED_FORM	9	Electabuzz	"When a storm arrives, gangs of this Pokémon compete with each other to scale heights that are likely to be stricken by lightning bolts. Some towns use Electabuzz in place of lightning rods."	Electric Pokémon
ELECTABUZZ_SHADOW_FORM	9	Electabuzz	"When a storm arrives, gangs of this Pokémon compete with each other to scale heights that are likely to be stricken by lightning bolts. Some towns use Electabuzz in place of lightning rods."	Electric Pokémon
ELECTIVIRE	9	Electivire	A single Electivire can provide enough electricity for all the buildings in a big city for a year.	Thunderbolt Pokémon
ELECTIVIRE_PURIFIED_FORM	9	Electivire	A single Electivire can provide enough electricity for all the buildings in a big city for a year.	Thunderbolt Pokémon
ELECTIVIRE_SHADOW_FORM	9	Electivire	A single Electivire can provide enough electricity for all the buildings in a big city for a year.	Thunderbolt Pokémon
ELECTRIKE	9	Electrike	Electrike stores electricity in its long body hair. This Pokémon stimulates its leg muscles with electric charges. These jolts of power give its legs explosive acceleration performance.	Lightning Pokémon
ELECTRODE	9	Electrode	"Electrode eats electricity in the atmosphere. On days when lightning strikes, you can see this Pokémon exploding all over the place from eating too much electricity."	Ball Pokémon
ELEKID	9	Elekid	"Elekid stores electricity in its body. If it touches metal and accidentally discharges all its built-up electricity, this Pokémon begins swinging its arms in circles to recharge itself."	Electric Pokémon
ELGYEM	9	Elgyem	This Pokémon is shrouded in mystery. It's said to have appeared from a UFO that fell from the sky about 50 years ago.	Cerebral Pokémon
EMBOAR	9	Emboar	It has mastered fast and powerful fighting moves. It grows a beard of fire.	Mega Fire Pig Pokémon
EMOLGA	9	Emolga	"As it flies, it scatters electricity around, so bird Pokémon keep their distance. That's why Emolga can keep all its food to itself."	Sky Squirrel Pokémon
EMPOLEON	9	Empoleon	The three horns that extend from its beak attest to its power. The leader has the biggest horns.	Emperor Pokémon
ENTEI	9	Entei	Entei embodies the passion of magma. This Pokémon is thought to have been born in the eruption of a volcano. It sends up massive bursts of fire that utterly consume all that they touch.	Volcano Pokémon
ESCAVALIER	9	Escavalier	These Pokémon evolve by wearing the shell covering of a Shelmet. The steel armor protects their whole body.	Cavalry Pokémon
ESPEON	9	Espeon	Espeon is extremely loyal to any Trainer it considers to be worthy. It is said that this Pokémon developed its precognitive powers to protect its Trainer from harm.	Sun Pokémon
EXCADRILL	9	Excadrill	"More than 300 feet below the surface, they build mazelike nests. Their activity can be destructive to subway tunnels."	Subterrene Pokémon
EXEGGCUTE	9	Exeggcute	"This Pokémon consists of six eggs that form a closely knit cluster. The six eggs attract each other and spin around. When cracks increasingly appear on the eggs, Exeggcute is close to evolution."	Egg Pokémon
EXEGGUTOR	9	Exeggutor	"Exeggutor originally came from the tropics. Its heads steadily grow larger from exposure to strong sunlight. It is said that when the heads fall off, they group together to form Exeggcute."	Coconut Pokémon
EXEGGUTOR_ALOLA_FORM	9	Exeggutor	"Exeggutor originally came from the tropics. Its heads steadily grow larger from exposure to strong sunlight. It is said that when the heads fall off, they group together to form Exeggcute."	Coconut Pokémon
EXPLOUD	9	Exploud	"Exploud triggers earthquakes with the tremors it creates by bellowing. If this Pokémon violently inhales from the ports on its body, it's a sign that it is preparing to let loose a huge bellow."	Loud Noise Pokémon
FARFETCHD	9	Farfetch'd	"Farfetch'd is always seen with a stalk from a plant of some sort. Apparently, there are good stalks and bad stalks. This Pokémon has been known to fight with others over stalks."	Wild Duck Pokémon
FARFETCHD_GALARIAN_FORM	9	Farfetch'd	"The stalks of leeks are thicker and longer in the Galar region. Farfetch'd that adapted to these stalks took on a unique form."	Wild Duck Pokémon
FEAROW	9	Fearow	Fearow is recognized by its long neck and elongated beak. They are conveniently shaped for catching prey in soil or water. It deftly moves its long and skinny beak to pluck prey.	Beak Pokémon
FEEBAS	9	Feebas	"Feebas's fins are ragged and tattered from the start of its life. Because of its shoddy appearance, this Pokémon is largely ignored. It is capable of living in both the sea and in rivers."	Fish Pokémon
GENESECT_CHILL_FORM	9	Genesect	This Pokémon existed 300 million years ago. Team Plasma altered it and attached a cannon to its back.	Paleozoic Pokémon
FERALIGATR	9	Feraligatr	"Feraligatr intimidates its foes by opening its huge mouth. In battle, it will kick the ground hard with its thick and powerful hind legs to charge at the foe at an incredible speed."	Big Jaw Pokémon
FERROSEED	9	Ferroseed	It absorbs the iron it finds in the rock while clinging to the ceiling. It shoots spikes when in danger.	Thorn Seed Pokémon
FERROTHORN	9	Ferrothorn	"They attach themselves to cave ceilings, firing steel spikes at targets passing beneath them."	Thorn Pod Pokémon
FINNEON	9	Finneon	It lures in prey with its shining tail fins. It stays near the surface during the day and moves to the depths when night falls.	Wing Fish Pokémon
FLAAFFY	9	Flaaffy	Flaaffy's wool quality changes so that it can generate a high amount of static electricity with a small amount of wool. The bare and slick parts of its hide are shielded against electricity.	Wool Pokémon
FLAAFFY_PURIFIED_FORM	9	Flaaffy	Flaaffy's wool quality changes so that it can generate a high amount of static electricity with a small amount of wool. The bare and slick parts of its hide are shielded against electricity.	Wool Pokémon
FLAAFFY_SHADOW_FORM	9	Flaaffy	Flaaffy's wool quality changes so that it can generate a high amount of static electricity with a small amount of wool. The bare and slick parts of its hide are shielded against electricity.	Wool Pokémon
FLAREON	9	Flareon	"Flareon's fluffy fur has a functional purpose—it releases heat into the air so that its body does not get excessively hot. This Pokémon's body temperature can rise to a maximum of 1,650 degrees Fahrenheit."	Flame Pokémon
FLOATZEL	9	Floatzel	Its flotation sac developed as a result of pursuing aquatic prey. It can double as a rubber raft.	Sea Weasel Pokémon
FLYGON	9	Flygon	"Flygon is nicknamed “the elemental spirit of the desert.” Because its flapping wings whip up a cloud of sand, this Pokémon is always enveloped in a sandstorm while flying."	Mystic Pokémon
FLYGON_PURIFIED_FORM	9	Flygon	"Flygon is nicknamed “the elemental spirit of the desert.” Because its flapping wings whip up a cloud of sand, this Pokémon is always enveloped in a sandstorm while flying."	Mystic Pokémon
FLYGON_SHADOW_FORM	9	Flygon	"Flygon is nicknamed “the elemental spirit of the desert.” Because its flapping wings whip up a cloud of sand, this Pokémon is always enveloped in a sandstorm while flying."	Mystic Pokémon
FOONGUS	9	Foongus	"It lures Pokémon with its pattern that looks just like a Poké Ball, then releases poison spores."	Mushroom Pokémon
FORRETRESS	9	Forretress	"Forretress conceals itself inside its hardened steel shell. The shell is opened when the Pokémon is catching prey, but it does so at such a quick pace that the shell's inside cannot be seen."	Bagworm Pokémon
FRAXURE	9	Fraxure	"A broken tusk will not grow back, so it diligently sharpens its tusks on river rocks after the end of a battle."	Axe Jaw Pokémon
FRILLISH	9	Frillish	"Using the invisible poison spikes on its veillike arms and legs, it paralyzes its enemies and causes them to drown."	Floating Pokémon
FROSLASS	9	Froslass	"It's said that on nights of terrible blizzards, it comes down to human settlements. If you hear it knocking at your door, do not open it!"	Snow Land Pokémon
MURKROW_PURIFIED_FORM	9	Murkrow	Murkrow was feared and loathed as the alleged bearer of ill fortune. This Pokémon shows strong interest in anything that sparkles or glitters. It will even try to steal rings from women.	Darkness Pokémon
FURRET	9	Furret	"Furret has a very slim build. When under attack, it can slickly squirm through narrow spaces and get away. In spite of its short limbs, this Pokémon is very nimble and fleet."	Long Body Pokémon
GABITE	9	Gabite	It sheds its skin and gradually grows larger. Its scales can be ground into a powder and used as raw materials for traditional medicine.	Cave Pokémon
GALLADE	9	Gallade	"A master of courtesy and swordsmanship, it fights using extending swords on its elbows."	Blade Pokémon
GALLADE_MEGA	9	Mega Gallade	"A master of courtesy and swordsmanship, it fights using extending swords on its elbows."	Blade Pokémon
GALLADE_PURIFIED_FORM	9	Gallade	"A master of courtesy and swordsmanship, it fights using extending swords on its elbows."	Blade Pokémon
GALLADE_SHADOW_FORM	9	Gallade	"A master of courtesy and swordsmanship, it fights using extending swords on its elbows."	Blade Pokémon
GALVANTULA	9	Galvantula	"When attacked, they create an electric barrier by spitting out many electrically charged threads."	EleSpider Pokémon
GARBODOR	9	Garbodor	"Some say the reason Garbodor in Alola are a little stronger than their counterparts elsewhere is the presence of Muk, their natural enemy."	Trash Heap Pokémon
GARCHOMP	9	Garchomp	Its fine scales don't just reduce wind resistance—their sharp edges also cause injury to any opponent who attacks it.	Mach Pokémon
GARCHOMP_MEGA	9	Mega Garchomp	Its fine scales don't just reduce wind resistance—their sharp edges also cause injury to any opponent who attacks it.	Mach Pokémon
GARDEVOIR	9	Gardevoir	"Gardevoir has the ability to read the future. If it senses impending danger to its Trainer, this Pokémon is said to unleash its psychokinetic energy at full power."	Embrace Pokémon
GARDEVOIR_MEGA	9	Mega Gardevoir	"Gardevoir has the ability to read the future. If it senses impending danger to its Trainer, this Pokémon is said to unleash its psychokinetic energy at full power."	Embrace Pokémon
GARDEVOIR_PURIFIED_FORM	9	Gardevoir	"Gardevoir has the ability to read the future. If it senses impending danger to its Trainer, this Pokémon is said to unleash its psychokinetic energy at full power."	Embrace Pokémon
GARDEVOIR_SHADOW_FORM	9	Gardevoir	"Gardevoir has the ability to read the future. If it senses impending danger to its Trainer, this Pokémon is said to unleash its psychokinetic energy at full power."	Embrace Pokémon
GASTLY	9	Gastly	"Gastly is largely composed of gaseous matter. When exposed to a strong wind, the gaseous body quickly dwindles away. Groups of this Pokémon cluster under the eaves of houses to escape the ravages of wind."	Gas Pokémon
GASTRODON_EAST_SEA_FORM	9	Gastrodon	"Their shape and color change, depending on their environment and diet. There are many of them at beaches where the waves are calm."	Sea Slug Pokémon
GASTRODON_WEST_SEA_FORM	9	Gastrodon	"Their shape and color change, depending on their environment and diet. There are many of them at beaches where the waves are calm."	Sea Slug Pokémon
GENESECT	9	Genesect	This Pokémon existed 300 million years ago. Team Plasma altered it and attached a cannon to its back.	Paleozoic Pokémon
COMFEY	9	Comfey	\N	\N
ORANGURU	9	Oranguru	\N	\N
GENESECT_DOUSE_FORM	9	Genesect	This Pokémon existed 300 million years ago. Team Plasma altered it and attached a cannon to its back.	Paleozoic Pokémon
GENESECT_SHOCK_FORM	9	Genesect	This Pokémon existed 300 million years ago. Team Plasma altered it and attached a cannon to its back.	Paleozoic Pokémon
GENGAR	9	Gengar	"Sometimes, on a dark night, your shadow thrown by a streetlight will suddenly and startlingly overtake you. It is actually a Gengar running past you, pretending to be your shadow."	Shadow Pokémon
GENGAR_MEGA	9	Mega Gengar	"It can pass through other dimensions and can appear anywhere. It caused a stir one time when it stuck just one leg out of a wall."	Shadow Pokémon
GEODUDE	9	Geodude	"The longer a Geodude lives, the more its edges are chipped and worn away, making it more rounded in appearance. However, this Pokémon's heart will remain hard, craggy, and rough always."	Rock Pokémon
GEODUDE_ALOLA_FORM	9	Geodude	"The longer a Geodude lives, the more its edges are chipped and worn away, making it more rounded in appearance. However, this Pokémon's heart will remain hard, craggy, and rough always."	Rock Pokémon
GIBLE	9	Gible	"Its original home is an area much hotter than Alola. If you're planning to live with one, your heating bill will soar."	Land Shark Pokémon
GIGALITH	9	Gigalith	It absorbs rays of sunlight and shoots out energy. It's usually lurking deep beneath the surface.	Compressed Pokémon
GIRAFARIG	9	Girafarig	"Girafarig's rear head also has a brain, but it is small. The rear head attacks in response to smells and sounds. Approaching this Pokémon from behind can cause the rear head to suddenly lash out and bite."	Long Neck Pokémon
GIRATINA	9	Giratina	It was banished for its violence. It silently gazed upon the old world from the Distortion World.	Renegade Pokémon
GIRATINA_ORIGIN_FORM	9	Giratina	It was banished for its violence. It silently gazed upon the old world from the Distortion World.	Renegade Pokémon
GLACEON	9	Glaceon	"It can instantaneously freeze any moisture that's around it, creating ice pellets to shoot at its prey."	Fresh Snow Pokémon
GLALIE	9	Glalie	"Glalie has a body made of rock, which it hardens with an armor of ice. This Pokémon has the ability to freeze moisture in the atmosphere into any shape it desires."	Face Pokémon
GLALIE_MEGA	9	Mega Glalie	"Glalie has a body made of rock, which it hardens with an armor of ice. This Pokémon has the ability to freeze moisture in the atmosphere into any shape it desires."	Face Pokémon
GLAMEOW	9	Glameow	"When it's happy, Glameow demonstrates beautiful movements of its tail, like a dancing ribbon."	Catty Pokémon
GLIGAR	9	Gligar	"Gligar glides through the air without a sound as if it were sliding. This Pokémon hangs on to the face of its foe using its clawed hind legs and the large pincers on its forelegs, then injects the prey with its poison barb."	Fly Scorpion Pokémon
GLISCOR	9	Gliscor	Its flight is soundless. It uses its lengthy tail to carry off its prey... Then its elongated fangs do the rest.	Fang Scorpion Pokémon
GLOOM	9	Gloom	"Gloom releases a foul fragrance from the pistil of its flower. When faced with danger, the stench worsens. If this Pokémon is feeling calm and secure, it does not release its usual stinky aroma."	Weed Pokémon
GLOOM_PURIFIED_FORM	9	Gloom	"Gloom releases a foul fragrance from the pistil of its flower. When faced with danger, the stench worsens. If this Pokémon is feeling calm and secure, it does not release its usual stinky aroma."	Weed Pokémon
GLOOM_SHADOW_FORM	9	Gloom	"Gloom releases a foul fragrance from the pistil of its flower. When faced with danger, the stench worsens. If this Pokémon is feeling calm and secure, it does not release its usual stinky aroma."	Weed Pokémon
GOLBAT	9	Golbat	"Golbat loves to drink the blood of living things. It is particularly active in the pitch black of night. This Pokémon flits around in the night skies, seeking fresh blood."	Bat Pokémon
GOLBAT_PURIFIED_FORM	9	Golbat	"Golbat loves to drink the blood of living things. It is particularly active in the pitch black of night. This Pokémon flits around in the night skies, seeking fresh blood."	Bat Pokémon
GOLBAT_SHADOW_FORM	9	Golbat	"Golbat loves to drink the blood of living things. It is particularly active in the pitch black of night. This Pokémon flits around in the night skies, seeking fresh blood."	Bat Pokémon
GOLDEEN	9	Goldeen	"Goldeen is a very beautiful Pokémon with fins that billow elegantly in water. However, don't let your guard down around this Pokémon—it could ram you powerfully with its horn."	Goldfish Pokémon
GOLDUCK	9	Golduck	The webbed flippers on its forelegs and hind legs and the streamlined body of Golduck give it frightening speed. This Pokémon is definitely much faster than even the most athletic swimmer.	Duck Pokémon
GOLDUCK_PURIFIED_FORM	9	Golduck	The webbed flippers on its forelegs and hind legs and the streamlined body of Golduck give it frightening speed. This Pokémon is definitely much faster than even the most athletic swimmer.	Duck Pokémon
GOLDUCK_SHADOW_FORM	9	Golduck	The webbed flippers on its forelegs and hind legs and the streamlined body of Golduck give it frightening speed. This Pokémon is definitely much faster than even the most athletic swimmer.	Duck Pokémon
GOLEM	9	Golem	"Golem live up on mountains. If there is a large earthquake, these Pokémon will come rolling down off the mountains en masse to the foothills below."	Megaton Pokémon
GOLEM_ALOLA_FORM	9	Golem	"Golem live up on mountains. If there is a large earthquake, these Pokémon will come rolling down off the mountains en masse to the foothills below."	Megaton Pokémon
GOLETT	9	Golett	"Although ancient people apparently built it by working with clay, the source of its energy is unclear."	Automaton Pokémon
GOLURK	9	Golurk	"When the seal on its chest is removed, it rages indiscriminately, turning the whole town around it into a mountain of rubble."	Automaton Pokémon
GOREBYSS	9	Gorebyss	"Gorebyss lives in the southern seas at extreme depths. Its body is built to withstand the enormous pressure of water at incredible depths. Because of this, this Pokémon's body is unharmed by ordinary attacks."	South Sea Pokémon
GOTHITA	9	Gothita	"They intently observe both Trainers and Pokémon. Apparently, they are looking at something that only Gothita can see."	Fixation Pokémon
GOTHITELLE	9	Gothitelle	They can predict the future from the placement and movement of the stars. They can see Trainers' life spans.	Astral Body Pokémon
GOTHORITA	9	Gothorita	"According to many old tales, it creates friends for itself by controlling sleeping children on starry nights."	Manipulate Pokémon
PASSIMIAN	9	Passimian	\N	\N
WIMPOD	9	Wimpod	\N	\N
GRANBULL	9	Granbull	"Granbull has a particularly well-developed lower jaw. The enormous fangs are heavy, causing the Pokémon to tip its head back for balance. Unless it is startled, it will not try to bite indiscriminately."	Fairy Pokémon
GRAVELER	9	Graveler	"Graveler grows by feeding on rocks. Apparently, it prefers to eat rocks that are covered in moss. This Pokémon eats its way through a ton of rocks on a daily basis."	Rock Pokémon
GRAVELER_ALOLA_FORM	9	Graveler	"Graveler grows by feeding on rocks. Apparently, it prefers to eat rocks that are covered in moss. This Pokémon eats its way through a ton of rocks on a daily basis."	Rock Pokémon
GRIMER	9	Grimer	"Grimer's sludgy and rubbery body can be forced through any opening, however small it may be. This Pokémon enters sewer pipes to drink filthy wastewater."	Sludge Pokémon
GRIMER_ALOLA_FORM	9	Grimer	"Grimer's sludgy and rubbery body can be forced through any opening, however small it may be. This Pokémon enters sewer pipes to drink filthy wastewater."	Sludge Pokémon
GRIMER_PURIFIED_FORM	9	Grimer	"Grimer's sludgy and rubbery body can be forced through any opening, however small it may be. This Pokémon enters sewer pipes to drink filthy wastewater."	Sludge Pokémon
GRIMER_SHADOW_FORM	9	Grimer	"Grimer's sludgy and rubbery body can be forced through any opening, however small it may be. This Pokémon enters sewer pipes to drink filthy wastewater."	Sludge Pokémon
GROTLE	9	Grotle	It knows where pure water wells up. It carries fellow Pokémon there on its back.	Grove Pokémon
GROTLE_PURIFIED_FORM	9	Grotle	It knows where pure water wells up. It carries fellow Pokémon there on its back.	Grove Pokémon
GROTLE_SHADOW_FORM	9	Grotle	It knows where pure water wells up. It carries fellow Pokémon there on its back.	Grove Pokémon
GROUDON	9	Groudon	"Groudon is said to be the personification of the land itself. Legends tell of its many clashes against Kyogre, as each sought to gain the power of nature."	Continent Pokémon
GROVYLE	9	Grovyle	The leaves growing out of Grovyle's body are convenient for camouflaging it from enemies in the forest. This Pokémon is a master at climbing trees in jungles.	Wood Gecko Pokémon
GROWLITHE	9	Growlithe	"Growlithe has a superb sense of smell. Once it smells anything, this Pokémon won't forget the scent, no matter what. It uses its advanced olfactory sense to determine the emotions of other living things."	Puppy Pokémon
GROWLITHE_PURIFIED_FORM	9	Growlithe	"Growlithe has a superb sense of smell. Once it smells anything, this Pokémon won't forget the scent, no matter what. It uses its advanced olfactory sense to determine the emotions of other living things."	Puppy Pokémon
GROWLITHE_SHADOW_FORM	9	Growlithe	"Growlithe has a superb sense of smell. Once it smells anything, this Pokémon won't forget the scent, no matter what. It uses its advanced olfactory sense to determine the emotions of other living things."	Puppy Pokémon
GRUMPIG	9	Grumpig	"Grumpig uses the black pearls on its body to amplify its psychic power waves for gaining total control over its foe. When this Pokémon uses its special power, its snorting breath grows labored."	Manipulate Pokémon
GULPIN	9	Gulpin	"Virtually all of Gulpin's body is its stomach. As a result, it can swallow something its own size. This Pokémon's stomach contains a special fluid that digests anything."	Stomach Pokémon
GURDURR	9	Gurdurr	This Pokémon is so muscular and strongly built that even a group of wrestlers could not make it budge an inch.	Muscular Pokémon
GYARADOS	9	Gyarados	"When Magikarp evolves into Gyarados, its brain cells undergo a structural transformation. It is said that this transformation is to blame for this Pokémon's wildly violent nature."	Atrocious Pokémon
GYARADOS_MEGA	9	Mega Gyarados	"Although it obeys its instinctive drive to destroy everything within its reach, it will respond to orders from a Trainer it truly trusts."	Atrocious Pokémon
GYARADOS_PURIFIED_FORM	9	Gyarados	"When Magikarp evolves into Gyarados, its brain cells undergo a structural transformation. It is said that this transformation is to blame for this Pokémon's wildly violent nature."	Atrocious Pokémon
GYARADOS_SHADOW_FORM	9	Gyarados	"When Magikarp evolves into Gyarados, its brain cells undergo a structural transformation. It is said that this transformation is to blame for this Pokémon's wildly violent nature."	Atrocious Pokémon
HAPPINY	9	Happiny	"When it sees something round and white, Happiny puts it into the pouch on its stomach. It sometimes becomes overloaded and can't move."	Playhouse Pokémon
HARIYAMA	9	Hariyama	"Hariyama practices its straight-arm slaps in any number of locations. One hit of this Pokémon's powerful, openhanded, straight-arm punches could snap a telephone pole in two."	Arm Thrust Pokémon
HAUNTER	9	Haunter	"Haunter is a dangerous Pokémon. If one beckons you while floating in darkness, you must never approach it. This Pokémon will try to lick you with its tongue and steal your life away."	Gas Pokémon
HAXORUS	9	Haxorus	Their sturdy tusks will stay sharp even if used to cut steel beams. These Pokémon are covered in hard armor.	Axe Jaw Pokémon
HEATMOR	9	Heatmor	"It draws in air through its tail, transforms it into fire, and uses it like a tongue. It melts Durant and eats them."	Anteater Pokémon
HEATRAN	9	Heatran	"Boiling blood, like magma, circulates through its body. It makes its dwelling place in volcanic caves."	Lava Dome Pokémon
HERACROSS	9	Heracross	"Heracross charges in a straight line at its foe, slips beneath the foe's grasp, and then scoops up and hurls the opponent with its mighty horn. This Pokémon even has enough power to topple a massive tree."	Single Horn Pokémon
HERACROSS_MEGA	9	Mega Heracross	"A tremendous influx of energy builds it up, but when Mega Evolution ends, Heracross is bothered by terrible soreness in its muscles."	Single Horn Pokémon
HERDIER	9	Herdier	"It has been living with people for so long that portrayals of it can be found on the walls of caves from long, long ago."	Loyal Dog Pokémon
HIPPOPOTAS	9	Hippopotas	It enshrouds itself with sand to protect itself from germs. It does not enjoy getting wet.	Hippo Pokémon
HIPPOWDON	9	Hippowdon	It blasts internally stored sand from ports on its body to create a towering twister for attack.	Heavyweight Pokémon
HITMONCHAN	9	Hitmonchan	Hitmonchan is said to possess the spirit of a boxer who had been working toward a world championship. This Pokémon has an indomitable spirit and will never give up in the face of adversity.	Punching Pokémon
HITMONCHAN_PURIFIED_FORM	9	Hitmonchan	Hitmonchan is said to possess the spirit of a boxer who had been working toward a world championship. This Pokémon has an indomitable spirit and will never give up in the face of adversity.	Punching Pokémon
HITMONCHAN_SHADOW_FORM	9	Hitmonchan	Hitmonchan is said to possess the spirit of a boxer who had been working toward a world championship. This Pokémon has an indomitable spirit and will never give up in the face of adversity.	Punching Pokémon
HITMONLEE	9	Hitmonlee	"Hitmonlee's legs freely contract and stretch. Using these springlike legs, it bowls over foes with devastating kicks. After battle, it rubs down its legs and loosens the muscles to overcome fatigue."	Kicking Pokémon
HITMONTOP	9	Hitmontop	"Hitmontop spins on its head at high speed, all the while delivering kicks. This technique is a remarkable mix of both offense and defense at the same time. The Pokémon travels faster spinning than it does walking."	Handstand Pokémon
HO_OH	9	Ho-Oh	Ho-Oh's feathers glow in seven colors depending on the angle at which they are struck by light. These feathers are said to bring happiness to the bearers. This Pokémon is said to live at the foot of a rainbow.	Rainbow Pokémon
HONCHKROW	9	Honchkrow	Its goons take care of most of the fighting for it. The only time it dirties its own hands is in delivering a final blow to finish off an opponent.	Big Boss Pokémon
HOOTHOOT	9	Hoothoot	"Hoothoot has an internal organ that senses and tracks the earth's rotation. Using this special organ, this Pokémon begins hooting at precisely the same time every day."	Owl Pokémon
HOPPIP	9	Hoppip	"This Pokémon drifts and floats with the wind. If it senses the approach of strong winds, Hoppip links its leaves with other Hoppip to prepare against being blown away."	Cottonweed Pokémon
HORSEA	9	Horsea	"Horsea eats small insects and moss off of rocks. If the ocean current turns fast, this Pokémon anchors itself by wrapping its tail around rocks or coral to prevent being washed away."	Dragon Pokémon
HOUNDOOM	9	Houndoom	"In a Houndoom pack, the one with its horns raked sharply toward the back serves a leadership role. These Pokémon choose their leader by fighting among themselves."	Dark Pokémon
HOUNDOOM_MEGA	9	Mega Houndoom	"Its red claws and the tips of its tail are melting from high internal temperatures that are painful to Houndoom itself."	Dark Pokémon
HOUNDOOM_PURIFIED_FORM	9	Houndoom	"In a Houndoom pack, the one with its horns raked sharply toward the back serves a leadership role. These Pokémon choose their leader by fighting among themselves."	Dark Pokémon
HOUNDOOM_SHADOW_FORM	9	Houndoom	"In a Houndoom pack, the one with its horns raked sharply toward the back serves a leadership role. These Pokémon choose their leader by fighting among themselves."	Dark Pokémon
HOUNDOUR	9	Houndour	Houndour hunt as a coordinated pack. They communicate with each other using a variety of cries to corner their prey. This Pokémon's remarkable teamwork is unparalleled.	Dark Pokémon
HOUNDOUR_PURIFIED_FORM	9	Houndour	Houndour hunt as a coordinated pack. They communicate with each other using a variety of cries to corner their prey. This Pokémon's remarkable teamwork is unparalleled.	Dark Pokémon
HOUNDOUR_SHADOW_FORM	9	Houndour	Houndour hunt as a coordinated pack. They communicate with each other using a variety of cries to corner their prey. This Pokémon's remarkable teamwork is unparalleled.	Dark Pokémon
HUNTAIL	9	Huntail	Huntail's presence went unnoticed by people for a long time because it lives at extreme depths in the sea. This Pokémon's eyes can see clearly even in the murky dark depths of the ocean.	Deep Sea Pokémon
HYDREIGON	9	Hydreigon	"It responds to movement by attacking. This scary, three-headed Pokémon devours everything in its path!"	Brutal Pokémon
HYPNO	9	Hypno	"Hypno holds a pendulum in its hand. The arcing movement and glitter of the pendulum lull the foe into a deep state of hypnosis. While this Pokémon searches for prey, it polishes the pendulum."	Hypnosis Pokémon
HYPNO_PURIFIED_FORM	9	Hypno	"Hypno holds a pendulum in its hand. The arcing movement and glitter of the pendulum lull the foe into a deep state of hypnosis. While this Pokémon searches for prey, it polishes the pendulum."	Hypnosis Pokémon
HYPNO_SHADOW_FORM	9	Hypno	"Hypno holds a pendulum in its hand. The arcing movement and glitter of the pendulum lull the foe into a deep state of hypnosis. While this Pokémon searches for prey, it polishes the pendulum."	Hypnosis Pokémon
IGGLYBUFF	9	Igglybuff	Igglybuff's vocal cords are not sufficiently developed. It would hurt its throat if it were to sing too much. This Pokémon gargles with freshwater from a clean stream.	Balloon Pokémon
ILLUMISE	9	Illumise	"Illumise attracts a swarm of Volbeat using a sweet fragrance. Once the Volbeat have gathered, this Pokémon leads the lit-up swarm in drawing geometric designs on the canvas of the night sky."	Firefly Pokémon
INFERNAPE	9	Infernape	It tosses its enemies around with agility. It uses all its limbs to fight in its own unique style.	Flame Pokémon
IVYSAUR	9	Ivysaur	"There is a bud on this Pokémon's back. To support its weight, Ivysaur's legs and trunk grow thick and strong. If it starts spending more time lying in the sunlight, it's a sign that the bud will bloom into a large flower soon."	Seed Pokémon
IVYSAUR_PURIFIED_FORM	9	Ivysaur	"There is a bud on this Pokémon's back. To support its weight, Ivysaur's legs and trunk grow thick and strong. If it starts spending more time lying in the sunlight, it's a sign that the bud will bloom into a large flower soon."	Seed Pokémon
IVYSAUR_SHADOW_FORM	9	Ivysaur	"There is a bud on this Pokémon's back. To support its weight, Ivysaur's legs and trunk grow thick and strong. If it starts spending more time lying in the sunlight, it's a sign that the bud will bloom into a large flower soon."	Seed Pokémon
JELLICENT	9	Jellicent	Fishermen are terrified of Jellicent. It's rumored to drag them into the sea and steal their lives away.	Floating Pokémon
JIGGLYPUFF	9	Jigglypuff	Jigglypuff's vocal cords can freely adjust the wavelength of its voice. This Pokémon uses this ability to sing at precisely the right wavelength to make its foes most drowsy.	Balloon Pokémon
JIRACHI	9	Jirachi	"A legend states that Jirachi will make true any wish that is written on notes attached to its head when it awakens. If this Pokémon senses danger, it will fight without awakening."	Wish Pokémon
JOLTEON	9	Jolteon	"Jolteon's cells generate a low level of electricity. This power is amplified by the static electricity of its fur, enabling the Pokémon to drop thunderbolts. The bristling fur is made of electrically charged needles."	Lightning Pokémon
JOLTIK	9	Joltik	"They attach themselves to large-bodied Pokémon and absorb static electricity, which they store in an electric pouch."	Attaching Pokémon
JUMPLUFF	9	Jumpluff	Jumpluff rides warm southern winds to cross the sea and fly to foreign lands. The Pokémon descends to the ground when it encounters cold air while it is floating.	Cottonweed Pokémon
JYNX	9	Jynx	"Jynx walks rhythmically, swaying and shaking its hips as if it were dancing. Its motions are so bouncingly alluring, people seeing it are compelled to shake their hips without giving any thought to what they are doing."	Human Shape Pokémon
KABUTO	9	Kabuto	"Kabuto is a Pokémon that has been regenerated from a fossil. However, in extremely rare cases, living examples have been discovered. The Pokémon has not changed at all for 300 million years."	Shellfish Pokémon
KABUTOPS	9	Kabutops	Kabutops swam underwater to hunt for its prey in ancient times. The Pokémon was apparently evolving from being a water dweller to living on land as evident from the beginnings of change in its gills and legs.	Shellfish Pokémon
KADABRA	9	Kadabra	Kadabra emits a peculiar alpha wave if it develops a headache. Only those people with a particularly strong psyche can hope to become a Trainer of this Pokémon.	Psi Pokémon
KADABRA_PURIFIED_FORM	9	Kadabra	Kadabra emits a peculiar alpha wave if it develops a headache. Only those people with a particularly strong psyche can hope to become a Trainer of this Pokémon.	Psi Pokémon
KADABRA_SHADOW_FORM	9	Kadabra	Kadabra emits a peculiar alpha wave if it develops a headache. Only those people with a particularly strong psyche can hope to become a Trainer of this Pokémon.	Psi Pokémon
KAKUNA	9	Kakuna	"Kakuna remains virtually immobile as it clings to a tree. However, on the inside, it is extremely busy as it prepares for its coming evolution. This is evident from how hot the shell becomes to the touch."	Cocoon Pokémon
KAKUNA_PURIFIED_FORM	9	Kakuna	"Kakuna remains virtually immobile as it clings to a tree. However, on the inside, it is extremely busy as it prepares for its coming evolution. This is evident from how hot the shell becomes to the touch."	Cocoon Pokémon
KAKUNA_SHADOW_FORM	9	Kakuna	"Kakuna remains virtually immobile as it clings to a tree. However, on the inside, it is extremely busy as it prepares for its coming evolution. This is evident from how hot the shell becomes to the touch."	Cocoon Pokémon
KANGASKHAN	9	Kangaskhan	"If you come across a young Kangaskhan playing by itself, you must never disturb it or attempt to catch it. The baby Pokémon's parent is sure to be in the area, and it will become violently enraged at you."	Parent Pokémon
KANGASKHAN_MEGA	9	Mega Kangaskhan	"Its child has grown rapidly, thanks to the energy of Mega Evolution. Mother and child show their harmonious teamwork in battle."	Parent Pokémon
KARRABLAST	9	Karrablast	For some reason they evolve when they receive electrical energy while they are attacking Shelmet.	Clamping Pokémon
KECLEON	9	Kecleon	Kecleon is capable of changing its body colors at will to blend in with its surroundings. There is one exception—this Pokémon can't change the zigzag pattern on its belly.	Color Swap Pokémon
KELDEO_ORDINARY_FORM	9	Keldeo	"When it is resolute, its body fills with power and it becomes swifter. Its jumps are then too fast to follow."	Colt Pokémon
KELDEO_RESOLUTE_FORM	9	Keldeo	"When it is resolute, its body fills with power and it becomes swifter. Its jumps are then too fast to follow."	Colt Pokémon
KINGDRA	9	Kingdra	Kingdra lives at extreme ocean depths that are otherwise uninhabited. It has long been believed that the yawning of this Pokémon creates spiraling ocean currents.	Dragon Pokémon
KINGLER	9	Kingler	"Kingler has an enormous, oversized claw. It waves this huge claw in the air to communicate with others. However, because the claw is so heavy, the Pokémon quickly tires."	Pincer Pokémon
KIRLIA	9	Kirlia	It is said that a Kirlia that is exposed to the positive emotions of its Trainer grows beautiful. This Pokémon controls psychokinetic powers with its highly developed brain.	Emotion Pokémon
KIRLIA_PURIFIED_FORM	9	Kirlia	It is said that a Kirlia that is exposed to the positive emotions of its Trainer grows beautiful. This Pokémon controls psychokinetic powers with its highly developed brain.	Emotion Pokémon
KIRLIA_SHADOW_FORM	9	Kirlia	It is said that a Kirlia that is exposed to the positive emotions of its Trainer grows beautiful. This Pokémon controls psychokinetic powers with its highly developed brain.	Emotion Pokémon
KLANG	9	Klang	"A minigear and big gear comprise its body. If the minigear it launches at a foe doesn't return, it will die."	Gear Pokémon
KLINK	9	Klink	The two minigears that mesh together are predetermined. Each will rebound from other minigears without meshing.	Gear Pokémon
KLINKLANG	9	Klinklang	Its red core functions as an energy tank. It fires the charged energy through its spikes into an area.	Gear Pokémon
KOFFING	9	Koffing	"If Koffing becomes agitated, it raises the toxicity of its internal gases and jets them out from all over its body. This Pokémon may also overinflate its round body, then explode."	Poison Gas Pokémon
KRABBY	9	Krabby	"Krabby live on beaches, burrowed inside holes dug into the sand. On sandy beaches with little in the way of food, these Pokémon can be seen squabbling with each other over territory."	River Crab Pokémon
KRICKETOT	9	Kricketot	"When its antennae hit each other, it sounds like the music of a xylophone."	Cricket Pokémon
KRICKETUNE	9	Kricketune	It signals its emotions with its melodies. Scientists are studying these melodic patterns.	Cricket Pokémon
KROKOROK	9	Krokorok	It buries some of its prey in the sand to use as emergency meals when its hunts are unsuccessful.	Desert Croc Pokémon
KROOKODILE	9	Krookodile	It conceals itself in sandstorms that Flygon whip up and waits patiently for prey to appear.	Intimidation Pokémon
KYOGRE	9	Kyogre	"Through Primal Reversion and with nature's full power, it will take back its true form. It can summon storms that cause the sea levels to rise."	Sea Basin Pokémon
KYUREM	9	Kyurem	"It generates a powerful, freezing energy inside itself, but its body became frozen when the energy leaked out."	Boundary Pokémon
KYUREM_BLACK_FORM	9	Kyurem	"It generates a powerful, freezing energy inside itself, but its body became frozen when the energy leaked out."	Boundary Pokémon
KYUREM_WHITE_FORM	9	Kyurem	"It generates a powerful, freezing energy inside itself, but its body became frozen when the energy leaked out."	Boundary Pokémon
LAIRON	9	Lairon	Lairon tempers its steel body by drinking highly nutritious mineral springwater until it is bloated. This Pokémon makes its nest close to springs of delicious water.	Iron Armor Pokémon
LAMPENT	9	Lampent	It arrives near the moment of death and steals spirit from the body.	Lamp Pokémon
LANDORUS_INCARNATE_FORM	9	Landorus	"From the forces of lightning and wind, it creates energy to give nutrients to the soil and make the land abundant."	Abundance Pokémon
GOLISOPOD	9	Golisopod	\N	\N
LANDORUS_THERIAN_FORM	9	Landorus	"From the forces of lightning and wind, it creates energy to give nutrients to the soil and make the land abundant."	Abundance Pokémon
LANTURN	9	Lanturn	Lanturn is nicknamed “the deep-sea star” for its illuminated antenna. This Pokémon produces light by causing a chemical reaction between bacteria and its bodily fluids inside the antenna.	Light Pokémon
LAPRAS	9	Lapras	"People have driven Lapras almost to the point of extinction. In the evenings, this Pokémon is said to sing plaintively as it seeks what few others of its kind still remain."	Transport Pokémon
LAPRAS_PURIFIED_FORM	9	Lapras	"People have driven Lapras almost to the point of extinction. In the evenings, this Pokémon is said to sing plaintively as it seeks what few others of its kind still remain."	Transport Pokémon
LAPRAS_SHADOW_FORM	9	Lapras	"People have driven Lapras almost to the point of extinction. In the evenings, this Pokémon is said to sing plaintively as it seeks what few others of its kind still remain."	Transport Pokémon
LARVESTA	9	Larvesta	"It protects itself with flame. Long years ago, people believed Larvesta had a nest on the sun."	Torch Pokémon
LARVITAR	9	Larvitar	"Larvitar is born deep under the ground. To come up to the surface, this Pokémon must eat its way through the soil above. Until it does so, Larvitar cannot see its parents."	Rock Skin Pokémon
LARVITAR_PURIFIED_FORM	9	Larvitar	"Larvitar is born deep under the ground. To come up to the surface, this Pokémon must eat its way through the soil above. Until it does so, Larvitar cannot see its parents."	Rock Skin Pokémon
LARVITAR_SHADOW_FORM	9	Larvitar	"Larvitar is born deep under the ground. To come up to the surface, this Pokémon must eat its way through the soil above. Until it does so, Larvitar cannot see its parents."	Rock Skin Pokémon
LATIAS	9	Latias	"Latias is highly sensitive to the emotions of people. If it senses any hostility, this Pokémon ruffles the feathers all over its body and cries shrilly to intimidate the foe."	Eon Pokémon
LATIAS_MEGA	9	Mega Latias	"Latias is highly sensitive to the emotions of people. If it senses any hostility, this Pokémon ruffles the feathers all over its body and cries shrilly to intimidate the foe."	Eon Pokémon
LATIOS	9	Latios	Latios has the ability to make others see an image of what it has seen or imagines in its head. This Pokémon is intelligent and understands human speech.	Eon Pokémon
LATIOS_MEGA	9	Mega Latios	Latios has the ability to make others see an image of what it has seen or imagines in its head. This Pokémon is intelligent and understands human speech.	Eon Pokémon
LEAFEON	9	Leafeon	It gets its nutrition from photosynthesis. It lives a quiet life deep in forests where clean rivers flow.	Verdant Pokémon
LEAVANNY	9	Leavanny	It keeps its eggs warm with heat from fermenting leaves. It also uses leaves to make warm wrappings for Sewaddle.	Nurturing Pokémon
LEDIAN	9	Ledian	"It is said that in lands with clean air, where the stars fill the sky, there live Ledian in countless numbers. There is a good reason for this—the Pokémon uses the light of the stars as its energy."	Five Star Pokémon
LEDYBA	9	Ledyba	Ledyba secretes an aromatic fluid from where its legs join its body. This fluid is used for communicating with others. This Pokémon conveys its feelings to others by altering the fluid's scent.	Five Star Pokémon
LICKILICKY	9	Lickilicky	It uses its tongue much more skillfully than its hands or its feet. It can deftly pick up a single small bean with its tongue.	Licking Pokémon
LICKITUNG	9	Lickitung	"Whenever Lickitung comes across something new, it will unfailingly give it a lick. It does so because it memorizes things by texture and by taste. It is somewhat put off by sour things."	Licking Pokémon
LIEPARD	9	Liepard	"Stealthily, it sneaks up on its target, striking from behind before its victim has a chance to react."	Cruel Pokémon
LILEEP	9	Lileep	Lileep became extinct approximately a hundred million years ago. This ancient Pokémon attaches itself to a rock on the seafloor and catches approaching prey using tentacles shaped like flower petals.	Sea Lily Pokémon
LILLIGANT	9	Lilligant	"It's well liked by other Pokémon because of its beauty. The flower on its head needs constant care, or it will soon wither and rot."	Flowering Pokémon
LILLIPUP	9	Lillipup	"This Pokémon is popular with beginners because it's intelligent, obedient to its Trainer's commands, and easy to raise."	Puppy Pokémon
LINOONE	9	Linoone	"Linoone always runs full speed and only in straight lines. If facing an obstacle, it makes a right-angle turn to evade it. This Pokémon is very challenged by gently curving roads."	Rushing Pokémon
LINOONE_GALARIAN_FORM	9	Linoone	"Linoone always runs full speed and only in straight lines. If facing an obstacle, it makes a right-angle turn to evade it. This Pokémon is very challenged by gently curving roads."	Rushing Pokémon
LITWICK	9	Litwick	"Litwick shines a light that absorbs the life energy of people and Pokémon, which becomes the fuel that it burns."	Candle Pokémon
LOMBRE	9	Lombre	"Lombre is nocturnal—it will get active after dusk. It is also a mischief maker. When this Pokémon spots anglers, it tugs on their fishing lines from beneath the surface and enjoys their consternation."	Jolly Pokémon
LOPUNNY	9	Lopunny	"It's notably wary and has a dislike of fighting, but at the same time, it can deliver powerful kicks with its lithe legs."	Rabbit Pokémon
LOPUNNY_MEGA	9	Mega Lopunny	"It's notably wary and has a dislike of fighting, but at the same time, it can deliver powerful kicks with its lithe legs."	Rabbit Pokémon
LOTAD	9	Lotad	"Lotad live in ponds and lakes, where they float on the surface. It grows weak if its broad leaf dies. On rare occasions, this Pokémon travels on land in search of clean water."	Water Weed Pokémon
LOUDRED	9	Loudred	Loudred's bellowing can completely decimate a wood-frame house. It uses its voice to punish its foes. This Pokémon's round ears serve as loudspeakers.	Big Voice Pokémon
LUCARIO	9	Lucario	"Lucario reads its opponent's feelings with its aura waves. It finds out things it would rather not know, so it gets stressed out easily."	Aura Pokémon
LUCARIO_MEGA	9	Mega Lucario	"Lucario reads its opponent's feelings with its aura waves. It finds out things it would rather not know, so it gets stressed out easily."	Aura Pokémon
LUDICOLO	9	Ludicolo	"Ludicolo begins dancing as soon as it hears cheerful, festive music. This Pokémon is said to appear when it hears the singing of children on hiking outings."	Carefree Pokémon
LUGIA	9	Lugia	"Lugia's wings pack devastating power—a light fluttering of its wings can blow apart regular houses. As a result, this Pokémon chooses to live out of sight deep under the sea."	Diving Pokémon
LUMINEON	9	Lumineon	They traverse the deep waters as if crawling over the seafloor. The fantastic lights of its fins shine like stars in the night sky.	Neon Pokémon
LUNATONE	9	Lunatone	"Lunatone was discovered at a location where a meteoroid fell. As a result, some people theorize that this Pokémon came from space. However, no one has been able to prove this theory so far."	Meteorite Pokémon
LUVDISC	9	Luvdisc	Luvdisc live in shallow seas in the tropics. This heart-shaped Pokémon earned its name by swimming after loving couples it spotted in the ocean's waves.	Rendezvous Pokémon
LUXIO	9	Luxio	Strong electricity courses through the tips of its sharp claws. A light scratch causes fainting in foes.	Spark Pokémon
LUXRAY	9	Luxray	Luxray's ability to see through objects comes in handy when it's scouting for danger.	Gleam Eyes Pokémon
MACHAMP	9	Machamp	"Machamp has the power to hurl anything aside. However, trying to do any work requiring care and dexterity causes its arms to get tangled. This Pokémon tends to leap into action before it thinks."	Superpower Pokémon
MACHOKE	9	Machoke	"Machoke's thoroughly toned muscles possess the hardness of steel. This Pokémon has so much strength, it can easily hold aloft a sumo wrestler on just one finger."	Superpower Pokémon
MACHOP	9	Machop	Machop's muscles are special—they never get sore no matter how much they are used in exercise. This Pokémon has sufficient power to hurl a hundred adult humans.	Superpower Pokémon
MAGBY	9	Magby	"Magby's state of health is determined by observing the fire it breathes. If the Pokémon is spouting yellow flames from its mouth, it is in good health. When it is fatigued, black smoke will be mixed in with the flames."	Live Coal Pokémon
MAGCARGO	9	Magcargo	Magcargo's shell is actually its skin that hardened as a result of cooling. Its shell is very brittle and fragile—just touching it causes it to crumble apart. This Pokémon returns to its original size by dipping itself in magma.	Lava Pokémon
MAGIKARP	9	Magikarp	Magikarp is a pathetic excuse for a Pokémon that is only capable of flopping and splashing. This behavior prompted scientists to undertake research into it.	Fish Pokémon
MAGIKARP_PURIFIED_FORM	9	Magikarp	Magikarp is a pathetic excuse for a Pokémon that is only capable of flopping and splashing. This behavior prompted scientists to undertake research into it.	Fish Pokémon
MAGIKARP_SHADOW_FORM	9	Magikarp	Magikarp is a pathetic excuse for a Pokémon that is only capable of flopping and splashing. This behavior prompted scientists to undertake research into it.	Fish Pokémon
MAGMAR	9	Magmar	"In battle, Magmar blows out intensely hot flames from all over its body to intimidate its opponent. This Pokémon's fiery bursts create heat waves that ignite grass and trees in its surroundings."	Spitfire Pokémon
MAGMAR_PURIFIED_FORM	9	Magmar	"In battle, Magmar blows out intensely hot flames from all over its body to intimidate its opponent. This Pokémon's fiery bursts create heat waves that ignite grass and trees in its surroundings."	Spitfire Pokémon
MAGMAR_SHADOW_FORM	9	Magmar	"In battle, Magmar blows out intensely hot flames from all over its body to intimidate its opponent. This Pokémon's fiery bursts create heat waves that ignite grass and trees in its surroundings."	Spitfire Pokémon
MAGMORTAR	9	Magmortar	"Magmortar takes down its enemies by shooting fireballs, which burn them to a blackened crisp. It avoids this method when hunting prey."	Blast Pokémon
MAGMORTAR_PURIFIED_FORM	9	Magmortar	"Magmortar takes down its enemies by shooting fireballs, which burn them to a blackened crisp. It avoids this method when hunting prey."	Blast Pokémon
MAGMORTAR_SHADOW_FORM	9	Magmortar	"Magmortar takes down its enemies by shooting fireballs, which burn them to a blackened crisp. It avoids this method when hunting prey."	Blast Pokémon
MAGNEMITE	9	Magnemite	"Magnemite attaches itself to power lines to feed on electricity. If your house has a power outage, check your circuit breakers. You may find a large number of this Pokémon clinging to the breaker box."	Magnet Pokémon
MAGNEMITE_PURIFIED_FORM	9	Magnemite	"Magnemite attaches itself to power lines to feed on electricity. If your house has a power outage, check your circuit breakers. You may find a large number of this Pokémon clinging to the breaker box."	Magnet Pokémon
MAGNEMITE_SHADOW_FORM	9	Magnemite	"Magnemite attaches itself to power lines to feed on electricity. If your house has a power outage, check your circuit breakers. You may find a large number of this Pokémon clinging to the breaker box."	Magnet Pokémon
MAGNETON	9	Magneton	"Magneton emits a powerful magnetic force that is fatal to mechanical devices. As a result, large cities sound sirens to warn citizens of large-scale outbreaks of this Pokémon."	Magnet Pokémon
MAGNETON_PURIFIED_FORM	9	Magneton	"Magneton emits a powerful magnetic force that is fatal to mechanical devices. As a result, large cities sound sirens to warn citizens of large-scale outbreaks of this Pokémon."	Magnet Pokémon
MAGNETON_SHADOW_FORM	9	Magneton	"Magneton emits a powerful magnetic force that is fatal to mechanical devices. As a result, large cities sound sirens to warn citizens of large-scale outbreaks of this Pokémon."	Magnet Pokémon
MAGNEZONE	9	Magnezone	There are still people who believe that this Pokémon came from outer space. It emanates a powerful magnetic field.	Magnet Area Pokémon
MAGNEZONE_PURIFIED_FORM	9	Magnezone	There are still people who believe that this Pokémon came from outer space. It emanates a powerful magnetic field.	Magnet Area Pokémon
MAGNEZONE_SHADOW_FORM	9	Magnezone	There are still people who believe that this Pokémon came from outer space. It emanates a powerful magnetic field.	Magnet Area Pokémon
MAKUHITA	9	Makuhita	"Makuhita is tenacious—it will keep getting up and attacking its foe however many times it is knocked down. Every time it gets back up, this Pokémon stores more energy in its body for evolving."	Guts Pokémon
MAMOSWINE	9	Mamoswine	Its impressive tusks are made of ice. The population thinned when it turned warm after the ice age.	Twin Tusk Pokémon
MANAPHY	9	Manaphy	It starts its life with a wondrous power that permits it to bond with any kind of Pokémon.	Seafaring Pokémon
MANDIBUZZ	9	Mandibuzz	"It's always searching for food for Vullaby. When it finds a weak Pokémon, Mandibuzz swoops it right off to its nest."	Bone Vulture Pokémon
MANECTRIC	9	Manectric	"Manectric is constantly discharging electricity from its mane. The sparks sometimes ignite forest fires. When it enters a battle, this Pokémon creates thunderclouds."	Discharge Pokémon
MESPRIT	9	Mesprit	It sleeps at the bottom of a lake. Its spirit is said to leave its body to fly on the lake's surface.	Emotion Pokémon
MANECTRIC_MEGA	9	Mega Manectric	"Manectric is constantly discharging electricity from its mane. The sparks sometimes ignite forest fires. When it enters a battle, this Pokémon creates thunderclouds."	Discharge Pokémon
MANKEY	9	Mankey	"When Mankey starts shaking and its nasal breathing turns rough, it's a sure sign that it is becoming angry. However, because it goes into a towering rage almost instantly, it is impossible for anyone to flee its wrath."	Pig Monkey Pokémon
MANTINE	9	Mantine	"On sunny days, schools of Mantine can be seen elegantly leaping over the sea's waves. This Pokémon is not bothered by the Remoraid that hitches rides."	Kite Pokémon
MANTYKE	9	Mantyke	Mantyke are friendly toward people and will approach boats closely. The patterns on their backs differ depending on their habitat.	Kite Pokémon
MARACTUS	9	Maractus	"Arid regions are their habitat. They move rhythmically, making a sound similar to maracas."	Cactus Pokémon
MAREEP	9	Mareep	"Mareep's fluffy coat of wool rubs together and builds a static charge. The more static electricity is charged, the more brightly the lightbulb at the tip of its tail glows."	Wool Pokémon
MAREEP_PURIFIED_FORM	9	Mareep	"Mareep's fluffy coat of wool rubs together and builds a static charge. The more static electricity is charged, the more brightly the lightbulb at the tip of its tail glows."	Wool Pokémon
MAREEP_SHADOW_FORM	9	Mareep	"Mareep's fluffy coat of wool rubs together and builds a static charge. The more static electricity is charged, the more brightly the lightbulb at the tip of its tail glows."	Wool Pokémon
MARILL	9	Marill	"Marill's oil-filled tail acts much like a life preserver. If you see just its tail bobbing on the water's surface, it's a sure indication that this Pokémon is diving beneath the water to feed on aquatic plants."	Aqua Mouse Pokémon
MAROWAK	9	Marowak	Marowak is the evolved form of a Cubone that has overcome its sadness at the loss of its mother and grown tough. This Pokémon's tempered and hardened spirit is not easily broken.	Bone Keeper Pokémon
MAROWAK_ALOLA_FORM	9	Marowak	Marowak is the evolved form of a Cubone that has overcome its sadness at the loss of its mother and grown tough. This Pokémon's tempered and hardened spirit is not easily broken.	Bone Keeper Pokémon
MAROWAK_PURIFIED_FORM	9	Marowak	Marowak is the evolved form of a Cubone that has overcome its sadness at the loss of its mother and grown tough. This Pokémon's tempered and hardened spirit is not easily broken.	Bone Keeper Pokémon
MAROWAK_SHADOW_FORM	9	Marowak	Marowak is the evolved form of a Cubone that has overcome its sadness at the loss of its mother and grown tough. This Pokémon's tempered and hardened spirit is not easily broken.	Bone Keeper Pokémon
MARSHTOMP	9	Marshtomp	"The surface of Marshtomp's body is enveloped by a thin, sticky film that enables it to live on land. This Pokémon plays in mud on beaches when the ocean tide is low."	Mud Fish Pokémon
MARSHTOMP_PURIFIED_FORM	9	Marshtomp	"The surface of Marshtomp's body is enveloped by a thin, sticky film that enables it to live on land. This Pokémon plays in mud on beaches when the ocean tide is low."	Mud Fish Pokémon
MARSHTOMP_SHADOW_FORM	9	Marshtomp	"The surface of Marshtomp's body is enveloped by a thin, sticky film that enables it to live on land. This Pokémon plays in mud on beaches when the ocean tide is low."	Mud Fish Pokémon
MASQUERAIN	9	Masquerain	Masquerain intimidates enemies with the eyelike patterns on its antennas. This Pokémon flaps its four wings to freely fly in any direction—even sideways and backwards—as if it were a helicopter.	Eyeball Pokémon
MAWILE	9	Mawile	"Mawile's huge jaws are actually steel horns that have been transformed. Its docile-looking face serves to lull its foe into letting down its guard. When the foe least expects it, Mawile chomps it with its gaping jaws."	Deceiver Pokémon
MAWILE_MEGA	9	Mega Mawile	"Mawile's huge jaws are actually steel horns that have been transformed. Its docile-looking face serves to lull its foe into letting down its guard. When the foe least expects it, Mawile chomps it with its gaping jaws."	Deceiver Pokémon
MEDICHAM	9	Medicham	"It is said that through meditation, Medicham heightens energy inside its body and sharpens its sixth sense. This Pokémon hides its presence by merging itself with fields and mountains."	Meditate Pokémon
MEDICHAM_MEGA	9	Mega Medicham	"It is said that through meditation, Medicham heightens energy inside its body and sharpens its sixth sense. This Pokémon hides its presence by merging itself with fields and mountains."	Meditate Pokémon
MEDITITE	9	Meditite	"Meditite undertakes rigorous mental training deep in the mountains. However, whenever it meditates, this Pokémon always loses its concentration and focus. As a result, its training never ends."	Meditate Pokémon
MEGANIUM	9	Meganium	"The fragrance of Meganium's flower soothes and calms emotions. In battle, this Pokémon gives off more of its becalming scent to blunt the foe's fighting spirit."	Herb Pokémon
MELMETAL	9	Melmetal	"Revered long ago for its capacity to create iron from nothing, for some reason it has come back to life after 3,000 years."	Hex Nut Pokémon
MELOETTA_ARIA_FORM	9	Meloetta	Its melodies are sung with a special vocalization method that can control the feelings of those who hear it.	Melody Pokémon
MELOETTA_PIROUETTE_FORM	9	Meloetta	Its melodies are sung with a special vocalization method that can control the feelings of those who hear it.	Melody Pokémon
MELTAN	9	Meltan	"It melts particles of iron and other metals found in the subsoil, so it can absorb them into its body of molten steel."	Hex Nut Pokémon
MEOWTH	9	Meowth	"Meowth withdraws its sharp claws into its paws to slinkily sneak about without making any incriminating footsteps. For some reason, this Pokémon loves shiny coins that glitter with light."	Scratch Cat Pokémon
MEOWTH_ALOLA_FORM	9	Meowth	"Meowth withdraws its sharp claws into its paws to slinkily sneak about without making any incriminating footsteps. For some reason, this Pokémon loves shiny coins that glitter with light."	Scratch Cat Pokémon
MEOWTH_GALARIAN_FORM	9	Meowth	"Meowth withdraws its sharp claws into its paws to slinkily sneak about without making any incriminating footsteps. For some reason, this Pokémon loves shiny coins that glitter with light."	Scratch Cat Pokémon
MEOWTH_PURIFIED_FORM	9	Meowth	"Meowth withdraws its sharp claws into its paws to slinkily sneak about without making any incriminating footsteps. For some reason, this Pokémon loves shiny coins that glitter with light."	Scratch Cat Pokémon
MEOWTH_SHADOW_FORM	9	Meowth	"Meowth withdraws its sharp claws into its paws to slinkily sneak about without making any incriminating footsteps. For some reason, this Pokémon loves shiny coins that glitter with light."	Scratch Cat Pokémon
SANDYGAST	9	Sandygast	\N	\N
METAGROSS	9	Metagross	"Metagross has four brains in total. Combined, the four brains can breeze through difficult calculations faster than a supercomputer. This Pokémon can float in the air by tucking in its four legs."	Iron Leg Pokémon
METAGROSS_MEGA	9	Mega Metagross	"Metagross has four brains in total. Combined, the four brains can breeze through difficult calculations faster than a supercomputer. This Pokémon can float in the air by tucking in its four legs."	Iron Leg Pokémon
METANG	9	Metang	"When two Beldum fuse together, Metang is formed. The brains of the Beldum are joined by a magnetic nervous system. By linking its brains magnetically, this Pokémon generates strong psychokinetic power."	Iron Claw Pokémon
METAPOD	9	Metapod	The shell covering this Pokémon's body is as hard as an iron slab. Metapod does not move very much. It stays still because it is preparing its soft innards for evolution inside the hard shell.	Cocoon Pokémon
MEW	9	Mew	"Mew is said to possess the genetic composition of all Pokémon. It is capable of making itself invisible at will, so it entirely avoids notice even if it approaches people."	New Species Pokémon
MEWTWO	9	Mewtwo	"Mewtwo is a Pokémon that was created by genetic manipulation. However, even though the scientific power of humans created this Pokémon's body, they failed to endow Mewtwo with a compassionate heart."	Genetic Pokémon
MEWTWO_A_FORM	9	Mewtwo	"Mewtwo is a Pokémon that was created by genetic manipulation. However, even though the scientific power of humans created this Pokémon's body, they failed to endow Mewtwo with a compassionate heart."	Genetic Pokémon
MEWTWO_MEGA_X	9	Mega Mewtwo X	"Psychic power has augmented its muscles. It has a grip strength of one ton and can sprint a hundred meters in two seconds flat!"	Genetic Pokémon
MEWTWO_MEGA_Y	9	Mega Mewtwo Y	"Despite its diminished size, its mental power has grown phenomenally. With a mere thought, it can smash a skyscraper to smithereens."	Genetic Pokémon
MIENFOO	9	Mienfoo	They seclude themselves in the mountains and devote themselves to training. The form of their kicks and chops differs from pack to pack.	Martial Arts Pokémon
MIENSHAO	9	Mienshao	"When Mienshao lets out a bizarre wail, you're in danger. A flurry of kicks and chops too fast to see is about to be unleashed!"	Martial Arts Pokémon
MIGHTYENA	9	Mightyena	Mightyena gives obvious signals when it is preparing to attack. It starts to growl deeply and then flattens its body. This Pokémon will bite savagely with its sharply pointed fangs.	Bite Pokémon
MILOTIC	9	Milotic	Milotic is said to be the most beautiful of all the Pokémon. It has the power to becalm such emotions as anger and hostility to quell bitter feuding.	Tender Pokémon
MILTANK	9	Miltank	Miltank gives over five gallons of milk on a daily basis. Its sweet milk is enjoyed by children and grown-ups alike. People who can't drink milk turn it into yogurt and eat it instead.	Milk Cow Pokémon
MIME_JR	9	Mime Jr.	"When this gifted mimic surprises an opponent, Mime Jr. feels so happy that it ends up forgetting it was imitating something."	Mime Pokémon
MINCCINO	9	Minccino	"When its tail has gotten dirty from self-cleaning or from cleaning its nest, Minccino spends a whole day washing its tail in clean spring water."	Chinchilla Pokémon
MINUN	9	Minun	Minun is more concerned about cheering on its partners than its own safety. It shorts out the electricity in its body to create brilliant showers of sparks to cheer on its teammates.	Cheering Pokémon
MISDREAVUS	9	Misdreavus	"Misdreavus frightens people with a creepy, sobbing cry. The Pokémon apparently uses its red spheres to absorb the fearful feelings of foes and turn them into nutrition."	Screech Pokémon
MISMAGIUS	9	Mismagius	Its muttered curses can cause awful headaches or terrifying visions that torment others.	Magical Pokémon
MOLTRES	9	Moltres	"Moltres is a Legendary Pokémon that has the ability to control fire. If this Pokémon is injured, it is said to dip its body in the molten magma of a volcano to burn and heal itself."	Flame Pokémon
MONFERNO	9	Monferno	It uses ceilings and walls to launch aerial attacks. Its fiery tail is but one weapon.	Playful Pokémon
MOTHIM	9	Mothim	It flutters around at night and steals honey from the Combee hive.	Moth Pokémon
MR_MIME	9	Mr. Mime	"Mr. Mime is a master of pantomime. Its gestures and motions convince watchers that something unseeable actually exists. Once the watchers are convinced, the unseeable thing exists as if it were real."	Barrier Pokémon
MUDKIP	9	Mudkip	"The fin on Mudkip's head acts as highly sensitive radar. Using this fin to sense movements of water and air, this Pokémon can determine what is taking place around it without using its eyes."	Mud Fish Pokémon
MUDKIP_PURIFIED_FORM	9	Mudkip	"The fin on Mudkip's head acts as highly sensitive radar. Using this fin to sense movements of water and air, this Pokémon can determine what is taking place around it without using its eyes."	Mud Fish Pokémon
MUDKIP_SHADOW_FORM	9	Mudkip	"The fin on Mudkip's head acts as highly sensitive radar. Using this fin to sense movements of water and air, this Pokémon can determine what is taking place around it without using its eyes."	Mud Fish Pokémon
MUK	9	Muk	From Muk's body seeps a foul fluid that gives off a nose-bendingly horrible stench. Just one drop of this Pokémon's body fluid can turn a pool stagnant and rancid.	Sludge Pokémon
MUK_ALOLA_FORM	9	Muk	From Muk's body seeps a foul fluid that gives off a nose-bendingly horrible stench. Just one drop of this Pokémon's body fluid can turn a pool stagnant and rancid.	Sludge Pokémon
MUK_PURIFIED_FORM	9	Muk	From Muk's body seeps a foul fluid that gives off a nose-bendingly horrible stench. Just one drop of this Pokémon's body fluid can turn a pool stagnant and rancid.	Sludge Pokémon
MUK_SHADOW_FORM	9	Muk	From Muk's body seeps a foul fluid that gives off a nose-bendingly horrible stench. Just one drop of this Pokémon's body fluid can turn a pool stagnant and rancid.	Sludge Pokémon
MUNCHLAX	9	Munchlax	"Anything that looks edible, Munchlax will go on and swallow whole. Its stomach is tough enough to handle it even if the food has gone rotten."	Big Eater Pokémon
MUNNA	9	Munna	"It eats the dreams of people and Pokémon. When it eats a pleasant dream, it expels pink-colored mist."	Dream Eater Pokémon
MURKROW	9	Murkrow	Murkrow was feared and loathed as the alleged bearer of ill fortune. This Pokémon shows strong interest in anything that sparkles or glitters. It will even try to steal rings from women.	Darkness Pokémon
MUSHARNA	9	Musharna	The dream mist coming from its forehead changes into many different colors depending on the dream that was eaten.	Drowsing Pokémon
PALOSSAND	9	Palossand	\N	\N
PYUKUMUKU	9	Pyukumuku	\N	\N
NATU	9	Natu	"Natu cannot fly because its wings are not yet fully grown. If your eyes meet with this Pokémon's eyes, it will stare back intently at you. But if you move even slightly, it will hop away to safety."	Tiny Bird Pokémon
NIDOKING	9	Nidoking	"Nidoking's thick tail packs enormously destructive power. With one swing, it can topple a metal transmission tower. Once this Pokémon goes on a rampage, there is no stopping it."	Drill Pokémon
NIDOQUEEN	9	Nidoqueen	Nidoqueen's body is encased in extremely hard scales. It is adept at sending foes flying with harsh tackles. This Pokémon is at its strongest when it is defending its young.	Drill Pokémon
NIDORAN_FEMALE	9	Nidoran♀	"Nidoran♀ has barbs that secrete a powerful poison. They are thought to have developed as protection for this small-bodied Pokémon. When enraged, it releases a horrible toxin from its horn."	Poison Pin Pokémon
NIDORAN_MALE	9	Nidoran♂	"Nidoran♂ has developed muscles for moving its ears. Thanks to them, the ears can be freely moved in any direction. Even the slightest sound does not escape this Pokémon's notice."	Poison Pin Pokémon
NIDORINA	9	Nidorina	"When Nidorina are with their friends or family, they keep their barbs tucked away to prevent hurting each other. This Pokémon appears to become nervous if separated from the others."	Poison Pin Pokémon
NIDORINO	9	Nidorino	"Nidorino has a horn that is harder than a diamond. If it senses a hostile presence, all the barbs on its back bristle up at once, and it challenges the foe with all its might."	Poison Pin Pokémon
NINCADA	9	Nincada	Nincada lives underground for many years in complete darkness. This Pokémon absorbs nutrients from the roots of trees. It stays motionless as it waits for evolution.	Trainee Pokémon
NINETALES	9	Ninetales	Ninetales casts a sinister light from its bright red eyes to gain total control over its foe's mind. This Pokémon is said to live for a thousand years.	Fox Pokémon
NINETALES_ALOLA_FORM	9	Ninetales	Ninetales casts a sinister light from its bright red eyes to gain total control over its foe's mind. This Pokémon is said to live for a thousand years.	Fox Pokémon
NINJASK	9	Ninjask	"Ninjask moves around at such a high speed that it cannot be seen, even while its crying can be clearly heard. For that reason, this Pokémon was long believed to be invisible."	Ninja Pokémon
NOCTOWL	9	Noctowl	"Noctowl never fails at catching prey in darkness. This Pokémon owes its success to its superior vision that allows it to see in minimal light, and to its soft, supple wings that make no sound in flight."	Owl Pokémon
NOSEPASS	9	Nosepass	"Nosepass's magnetic nose is always pointed to the north. If two of these Pokémon meet, they cannot turn their faces to each other when they are close because their magnetic noses repel one another."	Compass Pokémon
NUMEL	9	Numel	"Numel is extremely dull witted—it doesn't notice being hit. However, it can't stand hunger for even a second. This Pokémon's body is a seething cauldron of boiling magma."	Numb Pokémon
NUZLEAF	9	Nuzleaf	Nuzleaf live in densely overgrown forests. They occasionally venture out of the forest to startle people. This Pokémon dislikes having its long nose pinched.	Wily Pokémon
NUZLEAF_PURIFIED_FORM	9	Nuzleaf	Nuzleaf live in densely overgrown forests. They occasionally venture out of the forest to startle people. This Pokémon dislikes having its long nose pinched.	Wily Pokémon
NUZLEAF_SHADOW_FORM	9	Nuzleaf	Nuzleaf live in densely overgrown forests. They occasionally venture out of the forest to startle people. This Pokémon dislikes having its long nose pinched.	Wily Pokémon
OBSTAGOON	9	Obstagoon	"Its voice is staggering in volume. Obstagoon has a tendency to take on a threatening posture and shout—this move is known as Obstruct."	Blocking Pokémon
OCTILLERY	9	Octillery	"Octillery grabs onto its foe using its tentacles. This Pokémon tries to immobilize it before delivering the finishing blow. If the foe turns out to be too strong, Octillery spews ink to escape."	Jet Pokémon
ODDISH	9	Oddish	"During the daytime, Oddish buries itself in soil to absorb nutrients from the ground using its entire body. The more fertile the soil, the glossier its leaves become."	Weed Pokémon
ODDISH_PURIFIED_FORM	9	Oddish	"During the daytime, Oddish buries itself in soil to absorb nutrients from the ground using its entire body. The more fertile the soil, the glossier its leaves become."	Weed Pokémon
ODDISH_SHADOW_FORM	9	Oddish	"During the daytime, Oddish buries itself in soil to absorb nutrients from the ground using its entire body. The more fertile the soil, the glossier its leaves become."	Weed Pokémon
OMANYTE	9	Omanyte	"Omanyte is one of the ancient and long-since-extinct Pokémon that have been regenerated from fossils by people. If attacked by an enemy, it withdraws itself inside its hard shell."	Spiral Pokémon
OMASTAR	9	Omastar	"Omastar uses its tentacles to capture its prey. It is believed to have become extinct because its shell grew too large and heavy, causing its movements to become too slow and ponderous."	Spiral Pokémon
ONIX	9	Onix	"Onix has a magnet in its brain. It acts as a compass so that this Pokémon does not lose direction while it is tunneling. As it grows older, its body becomes increasingly rounder and smoother."	Rock Snake Pokémon
OSHAWOTT	9	Oshawott	"It fights using the scalchop on its stomach. In response to an attack, it retaliates immediately by slashing."	Sea Otter Pokémon
PACHIRISU	9	Pachirisu	A pair may be seen rubbing their cheek pouches together in an effort to share stored electricity.	EleSquirrel Pokémon
PALKIA	9	Palkia	It has the ability to distort space. It is described as a deity in Sinnoh-region mythology.	Spatial Pokémon
PALPITOAD	9	Palpitoad	"It lives in the water and on land. It uses its long, sticky tongue to immobilize its opponents."	Vibration Pokémon
PANPOUR	9	Panpour	The water stored inside the tuft on its head is full of nutrients. Plants that receive its water grow large.	Spray Pokémon
PANSAGE	9	Pansage	It's good at finding berries and gathers them from all over. It's kind enough to share them with friends.	Grass Monkey Pokémon
PANSEAR	9	Pansear	This Pokémon lives in caves in volcanoes. The fire within the tuft on its head can reach 600 degrees Fahrenheit.	High Temp Pokémon
PARAS	9	Paras	Paras has parasitic mushrooms growing on its back called tochukaso. They grow large by drawing nutrients from this Bug Pokémon host. They are highly valued as a medicine for extending life.	Mushroom Pokémon
PARASECT	9	Parasect	"Parasect is known to infest large trees en masse and drain nutrients from the lower trunk and roots. When an infested tree dies, they move onto another tree all at once."	Mushroom Pokémon
TYPE_NULL	9	Type: Null	\N	\N
PATRAT	9	Patrat	"Extremely cautious, one of them will always be on the lookout, but it won't notice a foe coming from behind."	Scout Pokémon
PAWNIARD	9	Pawniard	"It follows Bisharp's orders to a tee when it attacks enemies. After slashing an opponent, Pawniard clangs both of its blades together."	Sharp Blade Pokémon
PELIPPER	9	Pelipper	Pelipper is a flying transporter that carries small Pokémon and eggs inside its massive bill. This Pokémon builds its nest on steep cliffs facing the sea.	Water Bird Pokémon
PERRSERKER	9	Perrserker	"What appears to be an iron helmet is actually hardened hair. This Pokémon lives for the thrill of battle."	Viking Pokémon
PERSIAN	9	Persian	Persian has six bold whiskers that give it a look of toughness. The whiskers sense air movements to determine what is in the Pokémon's surrounding vicinity. It becomes docile if grabbed by the whiskers.	Classy Cat Pokémon
PERSIAN_ALOLA_FORM	9	Persian	Persian has six bold whiskers that give it a look of toughness. The whiskers sense air movements to determine what is in the Pokémon's surrounding vicinity. It becomes docile if grabbed by the whiskers.	Classy Cat Pokémon
PERSIAN_PURIFIED_FORM	9	Persian	Persian has six bold whiskers that give it a look of toughness. The whiskers sense air movements to determine what is in the Pokémon's surrounding vicinity. It becomes docile if grabbed by the whiskers.	Classy Cat Pokémon
PERSIAN_SHADOW_FORM	9	Persian	Persian has six bold whiskers that give it a look of toughness. The whiskers sense air movements to determine what is in the Pokémon's surrounding vicinity. It becomes docile if grabbed by the whiskers.	Classy Cat Pokémon
PETILIL	9	Petilil	"They prefer clean water and soil. When the environment they live in turns bad, the whole bunch will up and move to a new area."	Bulb Pokémon
PHANPY	9	Phanpy	"For its nest, Phanpy digs a vertical pit in the ground at the edge of a river. It marks the area around its nest with its trunk to let the others know that the area has been claimed."	Long Nose Pokémon
PHIONE	9	Phione	"It drifts in warm seas. It always returns to where it was born, no matter how far it may have drifted."	Sea Drifter Pokémon
PICHU	9	Pichu	Pichu charges itself with electricity more easily on days with thunderclouds or when the air is very dry. You can hear the crackling of static electricity coming off this Pokémon.	Tiny Mouse Pokémon
PIDGEOT	9	Pidgeot	"This Pokémon has a dazzling plumage of beautifully glossy feathers. Many Trainers are captivated by the striking beauty of the feathers on its head, compelling them to choose Pidgeot as their Pokémon."	Bird Pokémon
PIDGEOT_MEGA	9	Mega Pidgeot	"With its muscular strength now greatly increased, it can fly continuously for two weeks without resting."	Bird Pokémon
PIDGEOTTO	9	Pidgeotto	"Pidgeotto claims a large area as its own territory. This Pokémon flies around, patrolling its living space. If its territory is violated, it shows no mercy in thoroughly punishing the foe with its sharp claws."	Bird Pokémon
PIDGEY	9	Pidgey	"Pidgey has an extremely sharp sense of direction. It is capable of unerringly returning home to its nest, however far it may be removed from its familiar surroundings."	Tiny Bird Pokémon
PIDOVE	9	Pidove	These Pokémon live in cities. They are accustomed to people. Flocks often gather in parks and plazas.	Tiny Pigeon Pokémon
PIGNITE	9	Pignite	"When its internal fire flares up, its movements grow sharper and faster. When in trouble, it emits smoke."	Fire Pig Pokémon
PIKACHU	9	Pikachu	"Whenever Pikachu comes across something new, it blasts it with a jolt of electricity. If you come across a blackened berry, it's evidence that this Pokémon mistook the intensity of its charge."	Mouse Pokémon
PILOSWINE	9	Piloswine	Piloswine is covered by a thick coat of long hair that enables it to endure the freezing cold. This Pokémon uses its tusks to dig up food that has been buried under ice.	Swine Pokémon
PINECO	9	Pineco	"Pineco hangs from a tree branch and patiently waits for prey to come along. If the Pokémon is disturbed while eating by someone shaking its tree, it drops down to the ground and explodes with no warning."	Bagworm Pokémon
PINSIR	9	Pinsir	Pinsir is astoundingly strong. It can grip a foe weighing twice its weight in its horns and easily lift it. This Pokémon's movements turn sluggish in cold places.	Stag Beetle Pokémon
PINSIR_MEGA	9	Mega Pinsir	"With its vaunted horns, it can lift an opponent 10 times heavier than itself and fly about with ease."	Stag Beetle Pokémon
PIPLUP	9	Piplup	"Because it is very proud, it hates accepting food from people. Its thick down guards it from cold."	Penguin Pokémon
PLUSLE	9	Plusle	"Plusle always acts as a cheerleader for its partners. Whenever a teammate puts out a good effort in battle, this Pokémon shorts out its body to create the crackling noises of sparks to show its joy."	Cheering Pokémon
POLITOED	9	Politoed	"The curled hair on Politoed's head is proof of its status as a king. It is said that the longer and more curled the hair, the more respect this Pokémon earns from its peers."	Frog Pokémon
POLITOED_PURIFIED_FORM	9	Politoed	"The curled hair on Politoed's head is proof of its status as a king. It is said that the longer and more curled the hair, the more respect this Pokémon earns from its peers."	Frog Pokémon
POLITOED_SHADOW_FORM	9	Politoed	"The curled hair on Politoed's head is proof of its status as a king. It is said that the longer and more curled the hair, the more respect this Pokémon earns from its peers."	Frog Pokémon
POLIWAG	9	Poliwag	"Poliwag has a very thin skin. It is possible to see the Pokémon's spiral innards right through the skin. Despite its thinness, however, the skin is also very flexible. Even sharp fangs bounce right off it."	Tadpole Pokémon
POLIWAG_PURIFIED_FORM	9	Poliwag	"Poliwag has a very thin skin. It is possible to see the Pokémon's spiral innards right through the skin. Despite its thinness, however, the skin is also very flexible. Even sharp fangs bounce right off it."	Tadpole Pokémon
POLIWAG_SHADOW_FORM	9	Poliwag	"Poliwag has a very thin skin. It is possible to see the Pokémon's spiral innards right through the skin. Despite its thinness, however, the skin is also very flexible. Even sharp fangs bounce right off it."	Tadpole Pokémon
POLIWHIRL	9	Poliwhirl	"The surface of Poliwhirl's body is always wet and slick with a slimy fluid. Because of this slippery covering, it can easily slip and slide out of the clutches of any enemy in battle."	Tadpole Pokémon
POLIWHIRL_PURIFIED_FORM	9	Poliwhirl	"The surface of Poliwhirl's body is always wet and slick with a slimy fluid. Because of this slippery covering, it can easily slip and slide out of the clutches of any enemy in battle."	Tadpole Pokémon
SILVALLY	9	Silvally	\N	\N
POLIWHIRL_SHADOW_FORM	9	Poliwhirl	"The surface of Poliwhirl's body is always wet and slick with a slimy fluid. Because of this slippery covering, it can easily slip and slide out of the clutches of any enemy in battle."	Tadpole Pokémon
POLIWRATH	9	Poliwrath	"Poliwrath's highly developed, brawny muscles never grow fatigued, however much it exercises. It is so tirelessly strong, this Pokémon can swim back and forth across the ocean without effort."	Tadpole Pokémon
POLIWRATH_PURIFIED_FORM	9	Poliwrath	"Poliwrath's highly developed, brawny muscles never grow fatigued, however much it exercises. It is so tirelessly strong, this Pokémon can swim back and forth across the ocean without effort."	Tadpole Pokémon
POLIWRATH_SHADOW_FORM	9	Poliwrath	"Poliwrath's highly developed, brawny muscles never grow fatigued, however much it exercises. It is so tirelessly strong, this Pokémon can swim back and forth across the ocean without effort."	Tadpole Pokémon
PONYTA	9	Ponyta	Ponyta is very weak at birth. It can barely stand up. This Pokémon becomes stronger by stumbling and falling to keep up with its parent.	Fire Horse Pokémon
PONYTA_GALARIAN_FORM	9	Ponyta	"Its small horn hides a healing power. With a few rubs from this Pokémon's horn, any slight wound you have will be healed."	Unique Horn Pokémon
POOCHYENA	9	Poochyena	"At first sight, Poochyena takes a bite at anything that moves. This Pokémon chases after prey until the victim becomes exhausted. However, it may turn tail if the prey strikes back."	Bite Pokémon
PORYGON	9	Porygon	Porygon is capable of reverting itself entirely back to program data and entering cyberspace. This Pokémon is copy protected so it cannot be duplicated by copying.	Virtual Pokémon
PORYGON_PURIFIED_FORM	9	Porygon	Porygon is capable of reverting itself entirely back to program data and entering cyberspace. This Pokémon is copy protected so it cannot be duplicated by copying.	Virtual Pokémon
PORYGON_SHADOW_FORM	9	Porygon	Porygon is capable of reverting itself entirely back to program data and entering cyberspace. This Pokémon is copy protected so it cannot be duplicated by copying.	Virtual Pokémon
PORYGON_Z	9	Porygon-Z	"A faulty update was added to its programming. Its behavior is noticeably strange, so the experiment may have been a failure."	Virtual Pokémon
PORYGON_Z_PURIFIED_FORM	9	Porygon-Z	"A faulty update was added to its programming. Its behavior is noticeably strange, so the experiment may have been a failure."	Virtual Pokémon
PORYGON_Z_SHADOW_FORM	9	Porygon-Z	"A faulty update was added to its programming. Its behavior is noticeably strange, so the experiment may have been a failure."	Virtual Pokémon
PORYGON2	9	Porygon2	Porygon2 was created by humans using the power of science. The man-made Pokémon has been endowed with artificial intelligence that enables it to learn new gestures and emotions on its own.	Virtual Pokémon
PORYGON2_PURIFIED_FORM	9	Porygon2	Porygon2 was created by humans using the power of science. The man-made Pokémon has been endowed with artificial intelligence that enables it to learn new gestures and emotions on its own.	Virtual Pokémon
PORYGON2_SHADOW_FORM	9	Porygon2	Porygon2 was created by humans using the power of science. The man-made Pokémon has been endowed with artificial intelligence that enables it to learn new gestures and emotions on its own.	Virtual Pokémon
PRIMEAPE	9	Primeape	"When Primeape becomes furious, its blood circulation is boosted. In turn, its muscles are made even stronger. However, it also becomes much less intelligent at the same time."	Pig Monkey Pokémon
PRINPLUP	9	Prinplup	It lives a solitary life. Its wings deliver wicked blows that can snap even the thickest of trees.	Penguin Pokémon
PROBOPASS	9	Probopass	It uses three small units to catch prey and battle enemies. The main body mostly just gives orders.	Compass Pokémon
PSYDUCK	9	Psyduck	"Psyduck uses a mysterious power. When it does so, this Pokémon generates brain waves that are supposedly only seen in sleepers. This discovery spurred controversy among scholars."	Duck Pokémon
PSYDUCK_PURIFIED_FORM	9	Psyduck	"Psyduck uses a mysterious power. When it does so, this Pokémon generates brain waves that are supposedly only seen in sleepers. This discovery spurred controversy among scholars."	Duck Pokémon
PSYDUCK_SHADOW_FORM	9	Psyduck	"Psyduck uses a mysterious power. When it does so, this Pokémon generates brain waves that are supposedly only seen in sleepers. This discovery spurred controversy among scholars."	Duck Pokémon
PUPITAR	9	Pupitar	Pupitar creates a gas inside its body that it compresses and forcefully ejects to propel itself like a jet. The body is very durable—it avoids damage even if it hits solid steel.	Hard Shell Pokémon
PUPITAR_PURIFIED_FORM	9	Pupitar	Pupitar creates a gas inside its body that it compresses and forcefully ejects to propel itself like a jet. The body is very durable—it avoids damage even if it hits solid steel.	Hard Shell Pokémon
PUPITAR_SHADOW_FORM	9	Pupitar	Pupitar creates a gas inside its body that it compresses and forcefully ejects to propel itself like a jet. The body is very durable—it avoids damage even if it hits solid steel.	Hard Shell Pokémon
PURRLOIN	9	Purrloin	"They steal from people for fun, but their victims can't help but forgive them. Their deceptively cute act is perfect."	Devious Pokémon
PURUGLY	9	Purugly	"To make itself appear intimidatingly beefy, it tightly cinches its waist with its twin tails."	Tiger Cat Pokémon
QUAGSIRE	9	Quagsire	"Quagsire hunts for food by leaving its mouth wide open in water and waiting for its prey to blunder in unaware. Because the Pokémon does not move, it does not get very hungry."	Water Fish Pokémon
QUILAVA	9	Quilava	Quilava keeps its foes at bay with the intensity of its flames and gusts of superheated air. This Pokémon applies its outstanding nimbleness to dodge attacks even while scorching the foe with flames.	Volcano Pokémon
QWILFISH	9	Qwilfish	"Qwilfish sucks in water, inflating itself. This Pokémon uses the pressure of the water it swallowed to shoot toxic quills all at once from all over its body. It finds swimming somewhat challenging."	Balloon Pokémon
RAICHU	9	Raichu	"If the electrical sacs become excessively charged, Raichu plants its tail in the ground and discharges. Scorched patches of ground will be found near this Pokémon's nest."	Mouse Pokémon
RAICHU_ALOLA_FORM	9	Raichu	"If the electrical sacs become excessively charged, Raichu plants its tail in the ground and discharges. Scorched patches of ground will be found near this Pokémon's nest."	Mouse Pokémon
RAIKOU	9	Raikou	Raikou embodies the speed of lightning. The roars of this Pokémon send shock waves shuddering through the air and shake the ground as if lightning bolts had come crashing down.	Thunder Pokémon
RALTS	9	Ralts	"Ralts senses the emotions of people using the horns on its head. This Pokémon rarely appears before people. But when it does, it draws closer if it senses that the person has a positive disposition."	Feeling Pokémon
RALTS_PURIFIED_FORM	9	Ralts	"Ralts senses the emotions of people using the horns on its head. This Pokémon rarely appears before people. But when it does, it draws closer if it senses that the person has a positive disposition."	Feeling Pokémon
RALTS_SHADOW_FORM	9	Ralts	"Ralts senses the emotions of people using the horns on its head. This Pokémon rarely appears before people. But when it does, it draws closer if it senses that the person has a positive disposition."	Feeling Pokémon
RAMPARDOS	9	Rampardos	"This ancient Pokémon used headbutts skillfully. Its brain was really small, so some theories suggest that its stupidity led to its extinction."	Head Butt Pokémon
RAPIDASH	9	Rapidash	"Rapidash usually can be seen casually cantering in the fields and plains. However, when this Pokémon turns serious, its fiery manes flare and blaze as it gallops its way up to 150 mph."	Fire Horse Pokémon
RAPIDASH_GALARIAN_FORM	9	Rapidash	"Little can stand up to its psycho cut. Unleashed from this Pokémon's horn, the move will punch a hole right through a thick metal sheet."	Unique Horn Pokémon
RATICATE	9	Raticate	"Raticate's sturdy fangs grow steadily. To keep them ground down, it gnaws on rocks and logs. It may even chew on the walls of houses."	Mouse Pokémon
RATICATE_ALOLA_FORM	9	Raticate	"Raticate's sturdy fangs grow steadily. To keep them ground down, it gnaws on rocks and logs. It may even chew on the walls of houses."	Mouse Pokémon
RATICATE_PURIFIED_FORM	9	Raticate	"Raticate's sturdy fangs grow steadily. To keep them ground down, it gnaws on rocks and logs. It may even chew on the walls of houses."	Mouse Pokémon
RATICATE_SHADOW_FORM	9	Raticate	"Raticate's sturdy fangs grow steadily. To keep them ground down, it gnaws on rocks and logs. It may even chew on the walls of houses."	Mouse Pokémon
RATTATA	9	Rattata	"Rattata is cautious in the extreme. Even while it is asleep, it constantly listens by moving its ears around. It is not picky about where it lives—it will make its nest anywhere."	Mouse Pokémon
RATTATA_ALOLA_FORM	9	Rattata	"Rattata is cautious in the extreme. Even while it is asleep, it constantly listens by moving its ears around. It is not picky about where it lives—it will make its nest anywhere."	Mouse Pokémon
RATTATA_PURIFIED_FORM	9	Rattata	"Rattata is cautious in the extreme. Even while it is asleep, it constantly listens by moving its ears around. It is not picky about where it lives—it will make its nest anywhere."	Mouse Pokémon
RATTATA_SHADOW_FORM	9	Rattata	"Rattata is cautious in the extreme. Even while it is asleep, it constantly listens by moving its ears around. It is not picky about where it lives—it will make its nest anywhere."	Mouse Pokémon
RAYQUAZA	9	Rayquaza	Rayquaza is said to have lived for hundreds of millions of years. Legends remain of how it put to rest the clash between Kyogre and Groudon.	Sky High Pokémon
RAYQUAZA_MEGA	9	Mega Rayquaza	Rayquaza is said to have lived for hundreds of millions of years. Legends remain of how it put to rest the clash between Kyogre and Groudon.	Sky High Pokémon
REGICE	9	Regice	"Regice's body was made during an ice age. The deep-frozen body can't be melted, even by fire. This Pokémon controls frigid air of -328 degrees Fahrenheit."	Iceberg Pokémon
REGIGIGAS	9	Regigigas	There is an enduring legend that states this Pokémon towed continents with ropes.	Colossal Pokémon
REGIROCK	9	Regirock	"Regirock was sealed away by people long ago. If this Pokémon's body is damaged in battle, it is said to seek out suitable rocks on its own to repair itself."	Rock Peak Pokémon
REGISTEEL	9	Registeel	Registeel has a body that is harder than any kind of metal. Its body is apparently hollow. No one has any idea what this Pokémon eats.	Iron Pokémon
RELICANTH	9	Relicanth	Relicanth is a Pokémon species that existed for a hundred million years without ever changing its form. This ancient Pokémon feeds on microscopic organisms with its toothless mouth.	Longevity Pokémon
REMORAID	9	Remoraid	"Remoraid sucks in water, then expels it at high velocity using its abdominal muscles to shoot down flying prey. When evolution draws near, this Pokémon travels downstream from rivers."	Jet Pokémon
RESHIRAM	9	Reshiram	"When Reshiram's tail flares, the heat energy moves the atmosphere and changes the world's weather."	Vast White Pokémon
REUNICLUS	9	Reuniclus	"When Reuniclus shake hands, a network forms between their brains, increasing their psychic power."	Multiplying Pokémon
RHYDON	9	Rhydon	Rhydon's horn can crush even uncut diamonds. One sweeping blow of its tail can topple a building. This Pokémon's hide is extremely tough. Even direct cannon hits don't leave a scratch.	Drill Pokémon
RHYHORN	9	Rhyhorn	"Rhyhorn runs in a straight line, smashing everything in its path. It is not bothered even if it rushes headlong into a block of steel. This Pokémon may feel some pain from the collision the next day, however."	Spikes Pokémon
RHYPERIOR	9	Rhyperior	It puts rocks in holes in its palms and uses its muscles to shoot them. Geodude are shot at rare times.	Drill Pokémon
RIOLU	9	Riolu	"It uses waves called auras to communicate with others of its kind. It doesn't make any noise during this time, so its enemies can't detect it."	Emanation Pokémon
ROGGENROLA	9	Roggenrola	It was found in a fissure in a layer of exposed rock. The material that makes up its body is dirt from several hundred years ago.	Mantle Pokémon
ROSELIA	9	Roselia	Roselia shoots sharp thorns as projectiles at any opponent that tries to steal the flowers on its arms. The aroma of this Pokémon brings serenity to living things.	Thorn Pokémon
ROSERADE	9	Roserade	"With the movements of a dancer, it strikes with whips that are densely lined with poison thorns."	Bouquet Pokémon
ROTOM	9	Rotom	Its body is composed of plasma. It is known to infiltrate electronic devices and wreak havoc.	Plasma Pokémon
ROTOM_FAN_FORM	9	Rotom	Its body is composed of plasma. It is known to infiltrate electronic devices and wreak havoc.	Plasma Pokémon
ROTOM_FROST_FORM	9	Rotom	Its body is composed of plasma. It is known to infiltrate electronic devices and wreak havoc.	Plasma Pokémon
ROTOM_HEAT_FORM	9	Rotom	Its body is composed of plasma. It is known to infiltrate electronic devices and wreak havoc.	Plasma Pokémon
ROTOM_MOW_FORM	9	Rotom	Its body is composed of plasma. It is known to infiltrate electronic devices and wreak havoc.	Plasma Pokémon
SILVALLY_BUG_FORM	9	Silvally	\N	\N
RUFFLET	9	Rufflet	"Known as a natural-born warrior, soon after its hatching, it will challenge its parent to a fight in order to gain their acceptance."	Eaglet Pokémon
SABLEYE	9	Sableye	"Sableye lead quiet lives deep inside caverns. They are feared, however, because these Pokémon are thought to steal the spirits of people when their eyes burn with a sinister glow in the darkness."	Darkness Pokémon
SABLEYE_MEGA	9	Mega Sableye	"Sableye lead quiet lives deep inside caverns. They are feared, however, because these Pokémon are thought to steal the spirits of people when their eyes burn with a sinister glow in the darkness."	Darkness Pokémon
SABLEYE_PURIFIED_FORM	9	Sableye	"Sableye lead quiet lives deep inside caverns. They are feared, however, because these Pokémon are thought to steal the spirits of people when their eyes burn with a sinister glow in the darkness."	Darkness Pokémon
SABLEYE_SHADOW_FORM	9	Sableye	"Sableye lead quiet lives deep inside caverns. They are feared, however, because these Pokémon are thought to steal the spirits of people when their eyes burn with a sinister glow in the darkness."	Darkness Pokémon
SALAMENCE	9	Salamence	"Salamence came about as a result of a strong, long-held dream of growing wings. It is said that this powerful desire triggered a sudden mutation in this Pokémon's cells, causing it to sprout its magnificent wings."	Dragon Pokémon
SALAMENCE_MEGA	9	Mega Salamence	"Salamence came about as a result of a strong, long-held dream of growing wings. It is said that this powerful desire triggered a sudden mutation in this Pokémon's cells, causing it to sprout its magnificent wings."	Dragon Pokémon
SAMUROTT	9	Samurott	One swing of the sword incorporated in its armor can fell an opponent. A simple glare from one of them quiets everybody.	Formidable Pokémon
SANDILE	9	Sandile	"Sandile's still not good at hunting, so it mostly eats things that have collapsed in the desert. It's called ""the cleaner of the desert."""	Desert Croc Pokémon
SANDSHREW	9	Sandshrew	"Sandshrew's body is configured to absorb water without waste, enabling it to survive in an arid desert. This Pokémon curls up to protect itself from its enemies."	Mouse Pokémon
SANDSHREW_ALOLA_FORM	9	Sandshrew	"Sandshrew's body is configured to absorb water without waste, enabling it to survive in an arid desert. This Pokémon curls up to protect itself from its enemies."	Mouse Pokémon
SANDSHREW_PURIFIED_FORM	9	Sandshrew	"Sandshrew's body is configured to absorb water without waste, enabling it to survive in an arid desert. This Pokémon curls up to protect itself from its enemies."	Mouse Pokémon
SANDSHREW_SHADOW_FORM	9	Sandshrew	"Sandshrew's body is configured to absorb water without waste, enabling it to survive in an arid desert. This Pokémon curls up to protect itself from its enemies."	Mouse Pokémon
SANDSLASH	9	Sandslash	"Sandslash's body is covered by tough spikes, which are hardened sections of its hide. Once a year, the old spikes fall out, to be replaced with new spikes that grow out from beneath the old ones."	Mouse Pokémon
SANDSLASH_ALOLA_FORM	9	Sandslash	"Sandslash's body is covered by tough spikes, which are hardened sections of its hide. Once a year, the old spikes fall out, to be replaced with new spikes that grow out from beneath the old ones."	Mouse Pokémon
SANDSLASH_PURIFIED_FORM	9	Sandslash	"Sandslash's body is covered by tough spikes, which are hardened sections of its hide. Once a year, the old spikes fall out, to be replaced with new spikes that grow out from beneath the old ones."	Mouse Pokémon
SANDSLASH_SHADOW_FORM	9	Sandslash	"Sandslash's body is covered by tough spikes, which are hardened sections of its hide. Once a year, the old spikes fall out, to be replaced with new spikes that grow out from beneath the old ones."	Mouse Pokémon
SAWK	9	Sawk	Tying their belts gets them pumped and makes their punches more destructive. Disturbing their training angers them.	Karate Pokémon
SAWSBUCK_AUTUMN_FORM	9	Sawsbuck	"They migrate according to the seasons, so some people call Sawsbuck the harbingers of spring."	Season Pokémon
SAWSBUCK_SPRING_FORM	9	Sawsbuck	"They migrate according to the seasons, so some people call Sawsbuck the harbingers of spring."	Season Pokémon
SAWSBUCK_SUMMER_FORM	9	Sawsbuck	"They migrate according to the seasons, so some people call Sawsbuck the harbingers of spring."	Season Pokémon
SAWSBUCK_WINTER_FORM	9	Sawsbuck	"They migrate according to the seasons, so some people call Sawsbuck the harbingers of spring."	Season Pokémon
SCEPTILE	9	Sceptile	The leaves growing on Sceptile's body are very sharp edged. This Pokémon is very agile—it leaps all over the branches of trees and jumps on its foe from above or behind.	Forest Pokémon
SCEPTILE_MEGA	9	Mega Sceptile	"The leaves growing on Sceptile's body are very sharp edged. This Pokémon is very agile—it leaps all over the branches of trees and jumps on its foe from above or behind."	Forest Pokémon
SCIZOR	9	Scizor	Scizor has a body with the hardness of steel. It is not easily fazed by ordinary sorts of attacks. This Pokémon flaps its wings to regulate its body temperature.	Pincer Pokémon
SCIZOR_MEGA	9	Mega Scizor	"The excess energy that bathes this Pokémon keeps it in constant danger of overflow. It can't sustain a battle over long periods of time."	Pincer Pokémon
SCIZOR_PURIFIED_FORM	9	Scizor	Scizor has a body with the hardness of steel. It is not easily fazed by ordinary sorts of attacks. This Pokémon flaps its wings to regulate its body temperature.	Pincer Pokémon
SCIZOR_SHADOW_FORM	9	Scizor	Scizor has a body with the hardness of steel. It is not easily fazed by ordinary sorts of attacks. This Pokémon flaps its wings to regulate its body temperature.	Pincer Pokémon
SCOLIPEDE	9	Scolipede	"With quick movements, it chases down its foes, attacking relentlessly with its horns until it prevails."	Megapede Pokémon
SCRAFTY	9	Scrafty	It taunts its opponents by spitting. It has a certain territory that it never leaves its whole life long.	Hoodlum Pokémon
SCRAGGY	9	Scraggy	"It stretches its saggy skin up to its neck to protect itself. The saggier their skin, the more respect they garner."	Shedding Pokémon
SCYTHER	9	Scyther	"Scyther is blindingly fast. Its blazing speed enhances the effectiveness of the twin scythes on its forearms. This Pokémon's scythes are so effective, they can slice through thick logs in one wicked stroke."	Mantis Pokémon
SCYTHER_PURIFIED_FORM	9	Scyther	"Scyther is blindingly fast. Its blazing speed enhances the effectiveness of the twin scythes on its forearms. This Pokémon's scythes are so effective, they can slice through thick logs in one wicked stroke."	Mantis Pokémon
TURTWIG_SHADOW_FORM	9	Turtwig	"It undertakes photosynthesis with its body, making oxygen. The leaf on its head wilts if it is thirsty."	Tiny Leaf Pokémon
SCYTHER_SHADOW_FORM	9	Scyther	"Scyther is blindingly fast. Its blazing speed enhances the effectiveness of the twin scythes on its forearms. This Pokémon's scythes are so effective, they can slice through thick logs in one wicked stroke."	Mantis Pokémon
SEADRA	9	Seadra	Seadra sleeps after wriggling itself between the branches of coral. Those trying to harvest coral are occasionally stung by this Pokémon's poison barbs if they fail to notice it.	Dragon Pokémon
SEAKING	9	Seaking	"In the autumn, Seaking males can be seen performing courtship dances in riverbeds to woo females. During this season, this Pokémon's body coloration is at its most beautiful."	Goldfish Pokémon
SEALEO	9	Sealeo	Sealeo has the habit of always juggling on the tip of its nose anything it sees for the first time. This Pokémon occasionally entertains itself by balancing and rolling a Spheal on its nose.	Ball Roll Pokémon
SEEDOT	9	Seedot	"Seedot attaches itself to a tree branch using the top of its head. It sucks moisture from the tree while hanging off the branch. The more water it drinks, the glossier this Pokémon's body becomes."	Acorn Pokémon
SEEDOT_PURIFIED_FORM	9	Seedot	"Seedot attaches itself to a tree branch using the top of its head. It sucks moisture from the tree while hanging off the branch. The more water it drinks, the glossier this Pokémon's body becomes."	Acorn Pokémon
SEEDOT_SHADOW_FORM	9	Seedot	"Seedot attaches itself to a tree branch using the top of its head. It sucks moisture from the tree while hanging off the branch. The more water it drinks, the glossier this Pokémon's body becomes."	Acorn Pokémon
SEEL	9	Seel	"Seel hunts for prey in the frigid sea underneath sheets of ice. When it needs to breathe, it punches a hole through the ice with the sharply protruding section of its head."	Sea Lion Pokémon
SEISMITOAD	9	Seismitoad	They shoot paralyzing liquid from their head bumps. They use vibration to hurt their opponents.	Vibration Pokémon
SENTRET	9	Sentret	"When Sentret sleeps, it does so while another stands guard. The sentry wakes the others at the first sign of danger. When this Pokémon becomes separated from its pack, it becomes incapable of sleep due to fear."	Scout Pokémon
SERPERIOR	9	Serperior	It can stop its opponents' movements with just a glare. It takes in solar energy and boosts it internally.	Regal Pokémon
SERVINE	9	Servine	"When it gets dirty, its leaves can't be used in photosynthesis, so it always keeps itself clean."	Grass Snake Pokémon
SEVIPER	9	Seviper	Seviper shares a generations-long feud with Zangoose. The scars on its body are evidence of vicious battles. This Pokémon attacks using its sword-edged tail.	Fang Snake Pokémon
SEWADDLE	9	Sewaddle	"Since this Pokémon makes its own clothes out of leaves, it is a popular mascot for fashion designers."	Sewing Pokémon
SHARPEDO	9	Sharpedo	"Nicknamed 'the bully of the sea,' Sharpedo is widely feared. Its cruel fangs grow back immediately if they snap off. Just one of these Pokémon can thoroughly tear apart a supertanker."	Brutal Pokémon
SHARPEDO_MEGA	9	Mega Sharpedo	"Nicknamed 'the bully of the sea,' Sharpedo is widely feared. Its cruel fangs grow back immediately if they snap off. Just one of these Pokémon can thoroughly tear apart a supertanker."	Brutal Pokémon
SHAYMIN	9	Shaymin	The blooming of Gracidea flowers confers the power of flight upon it. Feelings of gratitude are the message it delivers.	Gratitude Pokémon
SHAYMIN_LAND_FORM	9	Shaymin	The blooming of Gracidea flowers confers the power of flight upon it. Feelings of gratitude are the message it delivers.	Gratitude Pokémon
SHAYMIN_SKY_FORM	9	Shaymin	The blooming of Gracidea flowers confers the power of flight upon it. Feelings of gratitude are the message it delivers.	Gratitude Pokémon
SHEDINJA	9	Shedinja	"Shedinja's hard body doesn't move—not even a twitch. In fact, its body appears to be merely a hollow shell. It is believed that this Pokémon will steal the spirit of anyone peering into its hollow body from its back."	Shed Pokémon
SHELGON	9	Shelgon	"Inside Shelgon's armor-like shell, cells are in the midst of transformation to create an entirely new body. This Pokémon's shell is extremely heavy, making its movements sluggish."	Endurance Pokémon
SHELLDER	9	Shellder	"At night, this Pokémon uses its broad tongue to burrow a hole in the seafloor sand and then sleep in it. While it is sleeping, Shellder closes its shell, but leaves its tongue hanging out."	Bivalve Pokémon
SHELLOS_EAST_SEA_FORM	9	Shellos	"When it senses danger, a purple liquid oozes out of it. The liquid is thought to be something like greasy sweat."	Sea Slug Pokémon
SHELLOS_WEST_SEA_FORM	9	Shellos	"When it senses danger, a purple liquid oozes out of it. The liquid is thought to be something like greasy sweat."	Sea Slug Pokémon
SHELMET	9	Shelmet	It evolves when bathed in an electric-like energy along with Karrablast. The reason is still unknown.	Snail Pokémon
SHIELDON	9	Shieldon	"Although its fossils can be found in layers of primeval rock, nothing but its face has ever been discovered."	Shield Pokémon
SHIFTRY	9	Shiftry	Shiftry is a mysterious Pokémon that is said to live atop towering trees dating back over a thousand years. It creates terrific windstorms with the fans it holds.	Wicked Pokémon
SHIFTRY_PURIFIED_FORM	9	Shiftry	Shiftry is a mysterious Pokémon that is said to live atop towering trees dating back over a thousand years. It creates terrific windstorms with the fans it holds.	Wicked Pokémon
SHIFTRY_SHADOW_FORM	9	Shiftry	Shiftry is a mysterious Pokémon that is said to live atop towering trees dating back over a thousand years. It creates terrific windstorms with the fans it holds.	Wicked Pokémon
SHINX	9	Shinx	All of its fur dazzles if danger is sensed. It flees while the foe is momentarily blinded.	Flash Pokémon
SHROOMISH	9	Shroomish	"Shroomish live in damp soil in the dark depths of forests. They are often found keeping still under fallen leaves. This Pokémon feeds on compost that is made up of fallen, rotted leaves."	Mushroom Pokémon
SHUCKLE	9	Shuckle	"Shuckle quietly hides itself under rocks, keeping its body concealed inside its hard shell while eating berries it has stored away. The berries mix with its body fluids to become a juice."	Mold Pokémon
SHUPPET	9	Shuppet	"Shuppet is attracted by feelings of jealousy and vindictiveness. If someone develops strong feelings of vengeance, this Pokémon will appear in a swarm and line up beneath the eaves of that person's home."	Puppet Pokémon
SHUPPET_PURIFIED_FORM	9	Shuppet	"Shuppet is attracted by feelings of jealousy and vindictiveness. If someone develops strong feelings of vengeance, this Pokémon will appear in a swarm and line up beneath the eaves of that person's home."	Puppet Pokémon
SILVALLY_DARK_FORM	9	Silvally	\N	\N
SHUPPET_SHADOW_FORM	9	Shuppet	"Shuppet is attracted by feelings of jealousy and vindictiveness. If someone develops strong feelings of vengeance, this Pokémon will appear in a swarm and line up beneath the eaves of that person's home."	Puppet Pokémon
SIGILYPH	9	Sigilyph	"The guardians of an ancient city, they always fly the same route while keeping watch for invaders."	Avianoid Pokémon
SILCOON	9	Silcoon	"Silcoon tethers itself to a tree branch using silk to keep from falling. There, this Pokémon hangs quietly while it awaits evolution. It peers out of the silk cocoon through a small hole."	Cocoon Pokémon
SIMIPOUR	9	Simipour	"It prefers places with clean water. When its tuft runs low, it replenishes it by siphoning up water with its tail."	Geyser Pokémon
SIMISAGE	9	Simisage	"Ill tempered, it fights by swinging its barbed tail around wildly. The leaf growing on its head is very bitter."	Thorn Monkey Pokémon
SIMISEAR	9	Simisear	"When it gets excited, embers rise from its head and tail and it gets hot. For some reason, it loves sweets."	Ember Pokémon
SKARMORY	9	Skarmory	"Skarmory is entirely encased in hard, protective armor. This Pokémon flies at close to 190 mph. It slashes foes with its wings that possess swordlike cutting edges."	Armor Bird Pokémon
SKIPLOOM	9	Skiploom	"Skiploom's flower blossoms when the temperature rises above 64 degrees Fahrenheit. How much the flower opens depends on the temperature. For that reason, this Pokémon is sometimes used as a thermometer."	Cottonweed Pokémon
SKITTY	9	Skitty	Skitty has the habit of becoming fascinated by moving objects and chasing them around. This Pokémon is known to chase after its own tail and become dizzy.	Kitten Pokémon
SKORUPI	9	Skorupi	It burrows under the sand to lie in wait for prey. Its tail claws can inject its prey with a savage poison.	Scorpion Pokémon
SKUNTANK	9	Skuntank	It sprays a stinky fluid from its tail. The fluid smells worse the longer it is allowed to fester.	Skunk Pokémon
SLAKING	9	Slaking	"Slaking spends all day lying down and lolling about. It eats grass growing within its reach. If it eats all the grass it can reach, this Pokémon reluctantly moves to another spot."	Lazy Pokémon
SLAKOTH	9	Slakoth	"Slakoth lolls around for over 20 hours every day. Because it moves so little, it does not need much food. This Pokémon's sole daily meal consists of just three leaves."	Slacker Pokémon
SLOWBRO	9	Slowbro	"Slowbro's tail has a Shellder firmly attached with a bite. As a result, the tail can't be used for fishing anymore. This causes Slowbro to grudgingly swim and catch prey instead."	Hermit Crab Pokémon
SLOWBRO_MEGA	9	Mega Slowbro	"Under the influence of Shellder's digestive fluids, Slowpoke has awakened, gaining a great deal of power–and a little motivation to boot."	Hermit Crab Pokémon
SLOWKING	9	Slowking	"Slowking undertakes research every day in an effort to solve the mysteries of the world. However, this Pokémon apparently forgets everything it has learned if the Shellder on its head comes off."	Royal Pokémon
SLOWPOKE	9	Slowpoke	"Slowpoke uses its tail to catch prey by dipping it in water at the side of a river. However, this Pokémon often forgets what it's doing and often spends entire days just loafing at water's edge."	Dopey Pokémon
SLOWPOKE_GALARIAN_FORM	9	Slowpoke	"Although this Pokémon is normally zoned out, its expression abruptly sharpens on occasion. The cause for this seems to lie in Slowpoke's diet."	Dopey Pokémon
SLUGMA	9	Slugma	"Molten magma courses throughout Slugma's circulatory system. If this Pokémon is chilled, the magma cools and hardens. Its body turns brittle and chunks fall off, reducing its size."	Lava Pokémon
SMEARGLE	9	Smeargle	"Smeargle marks the boundaries of its territory using a body fluid that leaks out from the tip of its tail. Over 5,000 different marks left by this Pokémon have been found."	Painter Pokémon
SMOOCHUM	9	Smoochum	"Smoochum actively runs about, but also falls quite often. Whenever the chance arrives, it will look for its reflection to make sure its face hasn't become dirty."	Kiss Pokémon
SNEASEL	9	Sneasel	Sneasel scales trees by punching its hooked claws into the bark. This Pokémon seeks out unguarded nests and steals eggs for food while the parents are away.	Sharp Claw Pokémon
SNEASEL_PURIFIED_FORM	9	Sneasel	Sneasel scales trees by punching its hooked claws into the bark. This Pokémon seeks out unguarded nests and steals eggs for food while the parents are away.	Sharp Claw Pokémon
SNEASEL_SHADOW_FORM	9	Sneasel	Sneasel scales trees by punching its hooked claws into the bark. This Pokémon seeks out unguarded nests and steals eggs for food while the parents are away.	Sharp Claw Pokémon
SNIVY	9	Snivy	"They photosynthesize by bathing their tails in sunlight. When they are not feeling well, their tails droop."	Grass Snake Pokémon
SNORLAX	9	Snorlax	Snorlax's typical day consists of nothing more than eating and sleeping. It is such a docile Pokémon that there are children who use its expansive belly as a place to play.	Sleeping Pokémon
SNORLAX_PURIFIED_FORM	9	Snorlax	Snorlax's typical day consists of nothing more than eating and sleeping. It is such a docile Pokémon that there are children who use its expansive belly as a place to play.	Sleeping Pokémon
SNORLAX_SHADOW_FORM	9	Snorlax	Snorlax's typical day consists of nothing more than eating and sleeping. It is such a docile Pokémon that there are children who use its expansive belly as a place to play.	Sleeping Pokémon
SNORUNT	9	Snorunt	"Snorunt live in regions with heavy snowfall. In seasons without snow, such as spring and summer, this Pokémon steals away to live quietly among stalactites and stalagmites deep in caverns."	Snow Hat Pokémon
SNOVER	9	Snover	"In the spring, it grows berries with the texture of frozen treats around its belly."	Frost Tree Pokémon
SNUBBULL	9	Snubbull	"By baring its fangs and making a scary face, Snubbull sends smaller Pokémon scurrying away in terror. However, this Pokémon seems a little sad at making its foes flee."	Fairy Pokémon
SOLOSIS	9	Solosis	They drive away attackers by unleashing psychic power. They can use telepathy to talk with others.	Cell Pokémon
SOLROCK	9	Solrock	"Solrock is a new species of Pokémon that is said to have fallen from space. It floats in air and moves silently. In battle, this Pokémon releases intensely bright light."	Meteorite Pokémon
SPEAROW	9	Spearow	"Spearow has a very loud cry that can be heard over half a mile away. If its high, keening cry is heard echoing all around, it is a sign that they are warning each other of danger."	Tiny Bird Pokémon
TYMPOLE	9	Tympole	"By vibrating its cheeks, it emits sound waves imperceptible to humans. It uses the rhythm of these sounds to talk."	Tadpole Pokémon
SPHEAL	9	Spheal	"Spheal is much faster rolling than walking to get around. When groups of this Pokémon eat, they all clap at once to show their pleasure. Because of this, their mealtimes are noisy."	Clap Pokémon
SPINARAK	9	Spinarak	The web spun by Spinarak can be considered its second nervous system. It is said that this Pokémon can determine what kind of prey is touching its web just by the tiny vibrations it feels through the web's strands.	String Spit Pokémon
SPINDA	9	Spinda	"All the Spinda that exist in the world are said to have utterly unique spot patterns. The shaky, tottering steps of this Pokémon give it the appearance of dancing."	Spot Panda Pokémon
SPIRITOMB	9	Spiritomb	It was bound to a fissure in an odd keystone as punishment for misdeeds 500 years ago.	Forbidden Pokémon
SPOINK	9	Spoink	"Spoink bounces around on its tail. The shock of its bouncing makes its heart pump. As a result, this Pokémon cannot afford to stop bouncing—if it stops, its heart will stop."	Bounce Pokémon
SQUIRTLE	9	Squirtle	"Squirtle's shell is not merely used for protection. The shell's rounded shape and the grooves on its surface help minimize resistance in water, enabling this Pokémon to swim at high speeds."	Tiny Turtle Pokémon
SQUIRTLE_PURIFIED_FORM	9	Squirtle	"Squirtle's shell is not merely used for protection. The shell's rounded shape and the grooves on its surface help minimize resistance in water, enabling this Pokémon to swim at high speeds."	Tiny Turtle Pokémon
SQUIRTLE_SHADOW_FORM	9	Squirtle	"Squirtle's shell is not merely used for protection. The shell's rounded shape and the grooves on its surface help minimize resistance in water, enabling this Pokémon to swim at high speeds."	Tiny Turtle Pokémon
STANTLER	9	Stantler	"Stantler's magnificent antlers were traded at high prices as works of art. As a result, this Pokémon was hunted close to extinction by those who were after the priceless antlers."	Big Horn Pokémon
STARAPTOR	9	Staraptor	"When Staravia evolve into Staraptor, they leave the flock to live alone. They have sturdy wings."	Predator Pokémon
STARAVIA	9	Staravia	It lives in forests and fields. Squabbles over territory occur when flocks collide.	Starling Pokémon
STARLY	9	Starly	"They flock around mountains and fields, chasing after bug Pokémon. Their singing is noisy and annoying."	Starling Pokémon
STARMIE	9	Starmie	"Starmie's center section—the core—glows brightly in seven colors. Because of its luminous nature, this Pokémon has been given the nickname “the gem of the sea.”"	Mysterious Pokémon
STARYU	9	Staryu	"Staryu's center section has an organ called the core that shines bright red. If you go to a beach toward the end of summer, the glowing cores of these Pokémon look like the stars in the sky."	Star Shape Pokémon
STEELIX	9	Steelix	Steelix lives even further underground than Onix. This Pokémon is known to dig toward the earth's core. There are records of this Pokémon reaching a depth of over six-tenths of a mile underground.	Iron Snake Pokémon
STEELIX_MEGA	9	Mega Steelix	"Steelix lives even further underground than Onix. This Pokémon is known to dig toward the earth's core. There are records of this Pokémon reaching a depth of over six-tenths of a mile underground."	Iron Snake Pokémon
STOUTLAND	9	Stoutland	"Its fur is long and thick. A long time ago in cold regions, every household kept a Stoutland."	Big-Hearted Pokémon
STUNFISK	9	Stunfisk	"It conceals itself in the mud of the seashore. Then it waits. When prey touch it, it delivers a jolt of electricity."	Trap Pokémon
STUNFISK_GALARIAN_FORM	9	Stunfisk	"It conceals itself in the mud of the seashore. Then it waits. When prey touch it, it delivers a jolt of electricity."	Trap Pokémon
STUNKY	9	Stunky	It protects itself by spraying a noxious fluid from its rear. The stench lingers for 24 hours.	Skunk Pokémon
SUDOWOODO	9	Sudowoodo	"Sudowoodo camouflages itself as a tree to avoid being attacked by enemies. However, because its hands remain green throughout the year, the Pokémon is easily identified as a fake during the winter."	Imitation Pokémon
SUICUNE	9	Suicune	Suicune embodies the compassion of a pure spring of water. It runs across the land with gracefulness. This Pokémon has the power to purify dirty water.	Aurora Pokémon
SUNFLORA	9	Sunflora	Sunflora converts solar energy into nutrition. It moves around actively in the daytime when it is warm. It stops moving as soon as the sun goes down for the night.	Sun Pokémon
SUNKERN	9	Sunkern	"Sunkern tries to move as little as it possibly can. It does so because it tries to conserve all the nutrients it has stored in its body for its evolution. It will not eat a thing, subsisting only on morning dew."	Seed Pokémon
SURSKIT	9	Surskit	"From the tips of its feet, Surskit secretes an oil that enables it to walk on water as if it were skating. This Pokémon feeds on microscopic organisms in ponds and lakes."	Pond Skater Pokémon
SWABLU	9	Swablu	Swablu has light and fluffy wings that are like cottony clouds. This Pokémon is not frightened of people. It lands on the heads of people and sits there like a cotton-fluff hat.	Cotton Bird Pokémon
SWADLOON	9	Swadloon	"It protects itself from the cold by wrapping up in leaves. It stays on the move, eating leaves in forests."	Leaf-Wrapped Pokémon
SWALOT	9	Swalot	"When Swalot spots prey, it spurts out a hideously toxic fluid from its pores and sprays the target. Once the prey has weakened, this Pokémon gulps it down whole with its cavernous mouth."	Poison Bag Pokémon
SWAMPERT	9	Swampert	Swampert is very strong. It has enough power to easily drag a boulder weighing more than a ton. This Pokémon also has powerful vision that lets it see even in murky water.	Mud Fish Pokémon
SWAMPERT_MEGA	9	Mega Swampert	Swampert is very strong. It has enough power to easily drag a boulder weighing more than a ton. This Pokémon also has powerful vision that lets it see even in murky water.	Mud Fish Pokémon
SWAMPERT_PURIFIED_FORM	9	Swampert	Swampert is very strong. It has enough power to easily drag a boulder weighing more than a ton. This Pokémon also has powerful vision that lets it see even in murky water.	Mud Fish Pokémon
SWAMPERT_SHADOW_FORM	9	Swampert	Swampert is very strong. It has enough power to easily drag a boulder weighing more than a ton. This Pokémon also has powerful vision that lets it see even in murky water.	Mud Fish Pokémon
SWANNA	9	Swanna	Swanna start to dance at dusk. The one dancing in the middle is the leader of the flock.	White Bird Pokémon
SWELLOW	9	Swellow	"Swellow flies high above our heads, making graceful arcs in the sky. This Pokémon dives at a steep angle as soon as it spots its prey. The hapless prey is tightly grasped by Swellow's clawed feet, preventing escape."	Swallow Pokémon
SWINUB	9	Swinub	Swinub roots for food by rubbing its snout against the ground. Its favorite food is a mushroom that grows under the cover of dead grass. This Pokémon occasionally roots out hot springs.	Pig Pokémon
SWOOBAT	9	Swoobat	Anyone who comes into contact with the ultrasonic waves emitted by a courting male experiences a positive mood shift.	Courting Pokémon
TAILLOW	9	Taillow	"Taillow courageously stands its ground against foes, however strong they may be. This gutsy Pokémon will remain defiant even after a loss. On the other hand, it cries loudly if it becomes hungry."	Tiny Swallow Pokémon
TANGELA	9	Tangela	"Tangela's vines snap off easily if they are grabbed. This happens without pain, allowing it to make a quick getaway. The lost vines are replaced by newly grown vines the very next day."	Vine Pokémon
TANGROWTH	9	Tangrowth	"Its vines grow so profusely that, in the warm season, you can't even see its eyes."	Vine Pokémon
TAUROS	9	Tauros	"This Pokémon is not satisfied unless it is rampaging at all times. If there is no opponent for Tauros to battle, it will charge at thick trees and knock them down to calm itself."	Wild Bull Pokémon
TEDDIURSA	9	Teddiursa	This Pokémon likes to lick its palms that are sweetened by being soaked in honey. Teddiursa concocts its own honey by blending fruits and pollen collected by Beedrill.	Little Bear Pokémon
TENTACOOL	9	Tentacool	"Tentacool's body is largely composed of water. If it is removed from the sea, it dries up like parchment. If this Pokémon happens to become dehydrated, put it back into the sea."	Jellyfish Pokémon
TENTACRUEL	9	Tentacruel	Tentacruel has large red orbs on its head. The orbs glow before lashing the vicinity with a harsh ultrasonic blast. This Pokémon's outburst creates rough waves around it.	Jellyfish Pokémon
TEPIG	9	Tepig	"It loves to eat roasted berries, but sometimes it gets too excited and burns them to a crisp."	Fire Pig Pokémon
TERRAKION	9	Terrakion	"Spoken of in legend, this Pokémon used its phenomenal power to destroy a castle in its effort to protect Pokémon."	Cavern Pokémon
THROH	9	Throh	"When it encounters a foe bigger than itself, it wants to throw it. It changes belts as it gets stronger."	Judo Pokémon
THUNDURUS_INCARNATE_FORM	9	Thundurus	"As it flies around, it shoots lightning all over the place and causes forest fires. It is therefore disliked."	Bolt Strike Pokémon
THUNDURUS_THERIAN_FORM	9	Thundurus	"As it flies around, it shoots lightning all over the place and causes forest fires. It is therefore disliked."	Bolt Strike Pokémon
TIMBURR	9	Timburr	"Always carrying squared logs, they help out with construction. As they grow, they carry bigger logs."	Muscular Pokémon
TIRTOUGA	9	Tirtouga	"Its hunting grounds encompassed a broad area, from the land to more than half a mile deep in the ocean."	Prototurtle Pokémon
TOGEKISS	9	Togekiss	It shares many blessings with people who respect one another's rights and avoid needless strife.	Jubilee Pokémon
TOGEPI	9	Togepi	"As its energy, Togepi uses the positive emotions of compassion and pleasure exuded by people and Pokémon. This Pokémon stores up feelings of happiness inside its shell, then shares them with others."	Spike Ball Pokémon
TOGETIC	9	Togetic	"Togetic is said to be a Pokémon that brings good fortune. When the Pokémon spots someone who is pure of heart, it is said to appear and share its happiness with that person."	Happiness Pokémon
TORCHIC	9	Torchic	"Torchic sticks with its Trainer, following behind with unsteady steps. This Pokémon breathes fire of over 1,800 degrees Fahrenheit, including fireballs that leave the foe scorched black."	Chick Pokémon
TORKOAL	9	Torkoal	"Torkoal digs through mountains in search of coal. If it finds some, it fills hollow spaces on its shell with the coal and burns it. If it is attacked, this Pokémon spouts thick black smoke to beat a retreat."	Coal Pokémon
TORNADUS_INCARNATE_FORM	9	Tornadus	"Tornadus expels massive energy from its tail, causing severe storms. Its power is great enough to blow houses away."	Cyclone Pokémon
TORNADUS_THERIAN_FORM	9	Tornadus	"Tornadus expels massive energy from its tail, causing severe storms. Its power is great enough to blow houses away."	Cyclone Pokémon
TORTERRA	9	Torterra	Small Pokémon occasionally gather on its unmoving back to begin building their nests.	Continent Pokémon
TORTERRA_PURIFIED_FORM	9	Torterra	Small Pokémon occasionally gather on its unmoving back to begin building their nests.	Continent Pokémon
TORTERRA_SHADOW_FORM	9	Torterra	Small Pokémon occasionally gather on its unmoving back to begin building their nests.	Continent Pokémon
TOTODILE	9	Totodile	"Despite the smallness of its body, Totodile's jaws are very powerful. While the Pokémon may think it is just playfully nipping, its bite has enough power to cause serious injury."	Big Jaw Pokémon
TOXICROAK	9	Toxicroak	Its knuckle claws secrete a toxin so vile that even a scratch could prove fatal.	Toxic Mouth Pokémon
TRANQUILL	9	Tranquill	"No matter where in the world it goes, it knows where its nest is, so it never gets separated from its Trainer."	Wild Pigeon Pokémon
TRAPINCH	9	Trapinch	"Trapinch's nest is a sloped, bowl-like pit dug in sand. This Pokémon patiently waits for prey to tumble down the pit. Its giant jaws have enough strength to crush even boulders."	Ant Pit Pokémon
TRAPINCH_PURIFIED_FORM	9	Trapinch	"Trapinch's nest is a sloped, bowl-like pit dug in sand. This Pokémon patiently waits for prey to tumble down the pit. Its giant jaws have enough strength to crush even boulders."	Ant Pit Pokémon
TRAPINCH_SHADOW_FORM	9	Trapinch	"Trapinch's nest is a sloped, bowl-like pit dug in sand. This Pokémon patiently waits for prey to tumble down the pit. Its giant jaws have enough strength to crush even boulders."	Ant Pit Pokémon
TREECKO	9	Treecko	Treecko has small hooks on the bottom of its feet that enable it to scale vertical walls. This Pokémon attacks by slamming foes with its thick tail.	Wood Gecko Pokémon
TROPIUS	9	Tropius	"The bunches of fruit around Tropius's neck are very popular with children. This Pokémon loves fruit, and eats it continuously. Apparently, its love for fruit resulted in its own outgrowth of fruit."	Fruit Pokémon
TRUBBISH	9	Trubbish	"If a young Pokémon or child breathes in the toxic gas that Trubbish belches out, it could be a life-threatening situation."	Trash Bag Pokémon
TURTWIG	9	Turtwig	"It undertakes photosynthesis with its body, making oxygen. The leaf on its head wilts if it is thirsty."	Tiny Leaf Pokémon
TURTWIG_PURIFIED_FORM	9	Turtwig	"It undertakes photosynthesis with its body, making oxygen. The leaf on its head wilts if it is thirsty."	Tiny Leaf Pokémon
SILVALLY_DRAGON_FORM	9	Silvally	\N	\N
TYNAMO	9	Tynamo	"One alone can emit only a trickle of electricity, so a group of them gathers to unleash a powerful electric shock."	EleFish Pokémon
TYPHLOSION	9	Typhlosion	Typhlosion obscures itself behind a shimmering heat haze that it creates using its intensely hot flames. This Pokémon creates blazing explosive blasts that burn everything to cinders.	Volcano Pokémon
TYRANITAR	9	Tyranitar	"Tyranitar is so overwhelmingly powerful, it can bring down a whole mountain to make its nest. This Pokémon wanders about in mountains seeking new opponents to fight."	Armor Pokémon
TYRANITAR_MEGA	9	Mega Tyranitar	"Due to the colossal power poured into it, this Pokémon's back split right open. Its destructive instincts are the only thing keeping it moving."	Armor Pokémon
TYRANITAR_PURIFIED_FORM	9	Tyranitar	"Tyranitar is so overwhelmingly powerful, it can bring down a whole mountain to make its nest. This Pokémon wanders about in mountains seeking new opponents to fight."	Armor Pokémon
TYRANITAR_SHADOW_FORM	9	Tyranitar	"Tyranitar is so overwhelmingly powerful, it can bring down a whole mountain to make its nest. This Pokémon wanders about in mountains seeking new opponents to fight."	Armor Pokémon
TYROGUE	9	Tyrogue	"Tyrogue becomes stressed out if it does not get to train every day. When raising this Pokémon, the Trainer must establish and uphold various training methods."	Scuffle Pokémon
UMBREON	9	Umbreon	Umbreon evolved as a result of exposure to the moon's waves. It hides silently in darkness and waits for its foes to make a move. The rings on its body glow when it leaps to attack.	Moonlight Pokémon
UNFEZANT	9	Unfezant	Males have plumage on their heads. They will never let themselves feel close to anyone other than their Trainers.	Proud Pokémon
UNOWN	9	Unown	"This Pokémon is shaped like ancient writing. It is a mystery as to which came first, the ancient writings or the various Unown. Research into this topic is ongoing but nothing is known."	Symbol Pokémon
URSARING	9	Ursaring	"In the forests inhabited by Ursaring, it is said that there are many streams and towering trees where they gather food. This Pokémon walks through its forest gathering food every day."	Hibernator Pokémon
UXIE	9	Uxie	It is said that its emergence gave humans the intelligence to improve their quality of life.	Knowledge Pokémon
VANILLISH	9	Vanillish	This hearty Pokémon survived the Ice Age. It's incredibly popular in very hot regions.	Icy Snow Pokémon
VANILLITE	9	Vanillite	"When the morning sun hit an icicle, it wished not to melt, and thus Vanillite was born. At night, it buries itself in snow to sleep."	Fresh Snow Pokémon
VANILLUXE	9	Vanilluxe	"Vanilluxe is born when two Vanillish, half-melted by the day's light, stick to each other and freeze together in the cold return of night."	Snowstorm Pokémon
VAPOREON	9	Vaporeon	Vaporeon underwent a spontaneous mutation and grew fins and gills that allow it to live underwater. This Pokémon has the ability to freely control water.	Bubble Jet Pokémon
VENIPEDE	9	Venipede	"Its bite injects a potent poison, enough to paralyze large bird Pokémon that try to prey on it."	Centipede Pokémon
VENOMOTH	9	Venomoth	"Venomoth is nocturnal—it is a Pokémon that only becomes active at night. Its favorite prey are small insects that gather around streetlights, attracted by the light in the darkness."	Poison Moth Pokémon
VENOMOTH_PURIFIED_FORM	9	Venomoth	"Venomoth is nocturnal—it is a Pokémon that only becomes active at night. Its favorite prey are small insects that gather around streetlights, attracted by the light in the darkness."	Poison Moth Pokémon
VENOMOTH_SHADOW_FORM	9	Venomoth	"Venomoth is nocturnal—it is a Pokémon that only becomes active at night. Its favorite prey are small insects that gather around streetlights, attracted by the light in the darkness."	Poison Moth Pokémon
VENONAT	9	Venonat	"Venonat is said to have evolved with a coat of thin, stiff hair that covers its entire body for protection. It possesses large eyes that never fail to spot even minuscule prey."	Insect Pokémon
VENONAT_PURIFIED_FORM	9	Venonat	"Venonat is said to have evolved with a coat of thin, stiff hair that covers its entire body for protection. It possesses large eyes that never fail to spot even minuscule prey."	Insect Pokémon
VENONAT_SHADOW_FORM	9	Venonat	"Venonat is said to have evolved with a coat of thin, stiff hair that covers its entire body for protection. It possesses large eyes that never fail to spot even minuscule prey."	Insect Pokémon
VENUSAUR	9	Venusaur	There is a large flower on Venusaur's back. The flower is said to take on vivid colors if it gets plenty of nutrition and sunlight. The flower's aroma soothes the emotions of people.	Seed Pokémon
VENUSAUR_MEGA	9	Mega Venusaur	"In order to support its flower, which has grown larger due to Mega Evolution, its back and legs have become stronger."	Seed Pokémon
VENUSAUR_PURIFIED_FORM	9	Venusaur	There is a large flower on Venusaur's back. The flower is said to take on vivid colors if it gets plenty of nutrition and sunlight. The flower's aroma soothes the emotions of people.	Seed Pokémon
VENUSAUR_SHADOW_FORM	9	Venusaur	There is a large flower on Venusaur's back. The flower is said to take on vivid colors if it gets plenty of nutrition and sunlight. The flower's aroma soothes the emotions of people.	Seed Pokémon
VESPIQUEN	9	Vespiquen	Its abdomen is a honeycomb for grubs. It raises its grubs on honey collected by Combee.	Beehive Pokémon
VIBRAVA	9	Vibrava	"To make prey faint, Vibrava generates ultrasonic waves by vigorously making its two wings vibrate. This Pokémon's ultrasonic waves are so powerful, they can bring on headaches in people."	Vibration Pokémon
VIBRAVA_PURIFIED_FORM	9	Vibrava	"To make prey faint, Vibrava generates ultrasonic waves by vigorously making its two wings vibrate. This Pokémon's ultrasonic waves are so powerful, they can bring on headaches in people."	Vibration Pokémon
VIBRAVA_SHADOW_FORM	9	Vibrava	"To make prey faint, Vibrava generates ultrasonic waves by vigorously making its two wings vibrate. This Pokémon's ultrasonic waves are so powerful, they can bring on headaches in people."	Vibration Pokémon
VICTINI	9	Victini	"When it shares the infinite energy it creates, that being's entire body will be overflowing with power."	Victory Pokémon
VICTREEBEL	9	Victreebel	"Victreebel has a long vine that extends from its head. This vine is waved and flicked about as if it were an animal to attract prey. When an unsuspecting prey draws near, this Pokémon swallows it whole."	Flycatcher Pokémon
WHIMSICOTT	9	Whimsicott	"Whimsicott doesn't live in a fixed location. It floats around on whirling winds, appearing all over the place to perform its mischief."	Windveiled Pokémon
VICTREEBEL_PURIFIED_FORM	9	Victreebel	"Victreebel has a long vine that extends from its head. This vine is waved and flicked about as if it were an animal to attract prey. When an unsuspecting prey draws near, this Pokémon swallows it whole."	Flycatcher Pokémon
VICTREEBEL_SHADOW_FORM	9	Victreebel	"Victreebel has a long vine that extends from its head. This vine is waved and flicked about as if it were an animal to attract prey. When an unsuspecting prey draws near, this Pokémon swallows it whole."	Flycatcher Pokémon
VIGOROTH	9	Vigoroth	Vigoroth is always itching and agitated to go on a wild rampage. It simply can't tolerate sitting still for even a minute. This Pokémon's stress level rises if it can't be moving constantly.	Wild Monkey Pokémon
VILEPLUME	9	Vileplume	"Vileplume's toxic pollen triggers atrocious allergy attacks. That's why it is advisable never to approach any attractive flowers in a jungle, however pretty they may be."	Flower Pokémon
VILEPLUME_PURIFIED_FORM	9	Vileplume	"Vileplume's toxic pollen triggers atrocious allergy attacks. That's why it is advisable never to approach any attractive flowers in a jungle, however pretty they may be."	Flower Pokémon
VILEPLUME_SHADOW_FORM	9	Vileplume	"Vileplume's toxic pollen triggers atrocious allergy attacks. That's why it is advisable never to approach any attractive flowers in a jungle, however pretty they may be."	Flower Pokémon
VIRIZION	9	Virizion	Legends say this Pokémon confounded opponents with its swift movements.	Grassland Pokémon
VOLBEAT	9	Volbeat	"With the arrival of night, Volbeat emits light from its tail. It communicates with others by adjusting the intensity and flashing of its light. This Pokémon is attracted by the sweet aroma of Illumise."	Firefly Pokémon
VOLCARONA	9	Volcarona	"According to legends, it was hatched from a flaming cocoon to save people and Pokémon that were suffering from the cold."	Sun Pokémon
VOLTORB	9	Voltorb	Voltorb was first sighted at a company that manufactures Poké Balls. The link between that sighting and the fact that this Pokémon looks very similar to a Poké Ball remains a mystery.	Ball Pokémon
VULLABY	9	Vullaby	Its healthy appetite leads to visible growth spurts. It often has to replace the bones it wears as its size increases.	Diapered Pokémon
VULPIX	9	Vulpix	"At the time of its birth, Vulpix has one white tail. The tail separates into six if this Pokémon receives plenty of love from its Trainer. The six tails become magnificently curled."	Fox Pokémon
VULPIX_ALOLA_FORM	9	Vulpix	"At the time of its birth, Vulpix has one white tail. The tail separates into six if this Pokémon receives plenty of love from its Trainer. The six tails become magnificently curled."	Fox Pokémon
WAILMER	9	Wailmer	Wailmer's nostrils are located above its eyes. This playful Pokémon loves to startle people by forcefully snorting out seawater it stores inside its body out of its nostrils.	Ball Whale Pokémon
WAILORD	9	Wailord	"Wailord is the largest of all identified Pokémon up to now. This giant Pokémon swims languorously in the vast open sea, eating massive amounts of food at once with its enormous mouth."	Float Whale Pokémon
WALREIN	9	Walrein	Walrein's two massively developed tusks can totally shatter blocks of ice weighing 10 tons with one blow. This Pokémon's thick coat of blubber insulates it from subzero temperatures.	Ice Break Pokémon
WARTORTLE	9	Wartortle	"Its tail is large and covered with a rich, thick fur. The tail becomes increasingly deeper in color as Wartortle ages. The scratches on its shell are evidence of this Pokémon's toughness as a battler."	Turtle Pokémon
WARTORTLE_PURIFIED_FORM	9	Wartortle	"Its tail is large and covered with a rich, thick fur. The tail becomes increasingly deeper in color as Wartortle ages. The scratches on its shell are evidence of this Pokémon's toughness as a battler."	Turtle Pokémon
WARTORTLE_SHADOW_FORM	9	Wartortle	"Its tail is large and covered with a rich, thick fur. The tail becomes increasingly deeper in color as Wartortle ages. The scratches on its shell are evidence of this Pokémon's toughness as a battler."	Turtle Pokémon
WATCHOG	9	Watchog	"When they see an enemy, their tails stand high, and they spit the seeds of berries stored in their cheek pouches."	Lookout Pokémon
WEAVILE	9	Weavile	"Thanks to its increased intelligence, scrapping over food is a thing of the past. A scratch from its claws will give you a case of frostbite!"	Sharp Claw Pokémon
WEAVILE_PURIFIED_FORM	9	Weavile	"Thanks to its increased intelligence, scrapping over food is a thing of the past. A scratch from its claws will give you a case of frostbite!"	Sharp Claw Pokémon
WEAVILE_SHADOW_FORM	9	Weavile	"Thanks to its increased intelligence, scrapping over food is a thing of the past. A scratch from its claws will give you a case of frostbite!"	Sharp Claw Pokémon
WEEDLE	9	Weedle	Weedle has an extremely acute sense of smell. It is capable of distinguishing its favorite kinds of leaves from those it dislikes just by sniffing with its big red proboscis (nose).	Hairy Bug Pokémon
WEEDLE_PURIFIED_FORM	9	Weedle	Weedle has an extremely acute sense of smell. It is capable of distinguishing its favorite kinds of leaves from those it dislikes just by sniffing with its big red proboscis (nose).	Hairy Bug Pokémon
WEEDLE_SHADOW_FORM	9	Weedle	Weedle has an extremely acute sense of smell. It is capable of distinguishing its favorite kinds of leaves from those it dislikes just by sniffing with its big red proboscis (nose).	Hairy Bug Pokémon
WEEPINBELL	9	Weepinbell	"Weepinbell has a large hook on its rear end. At night, the Pokémon hooks on to a tree branch and goes to sleep. If it moves around in its sleep, it may wake up to find itself on the ground."	Flycatcher Pokémon
WEEPINBELL_PURIFIED_FORM	9	Weepinbell	"Weepinbell has a large hook on its rear end. At night, the Pokémon hooks on to a tree branch and goes to sleep. If it moves around in its sleep, it may wake up to find itself on the ground."	Flycatcher Pokémon
WEEPINBELL_SHADOW_FORM	9	Weepinbell	"Weepinbell has a large hook on its rear end. At night, the Pokémon hooks on to a tree branch and goes to sleep. If it moves around in its sleep, it may wake up to find itself on the ground."	Flycatcher Pokémon
WEEZING	9	Weezing	"Weezing loves the gases given off by rotted kitchen garbage. This Pokémon will find a dirty, unkempt house and make it its home. At night, when the people in the house are asleep, it will go through the trash."	Poison Gas Pokémon
WEEZING_GALARIAN_FORM	9	Weezing	"Weezing loves the gases given off by rotted kitchen garbage. This Pokémon will find a dirty, unkempt house and make it its home. At night, when the people in the house are asleep, it will go through the trash."	Poison Gas Pokémon
WHIRLIPEDE	9	Whirlipede	"It is usually motionless, but when attacked, it rotates at high speed and then crashes into its opponent."	Curlipede Pokémon
WHISCASH	9	Whiscash	"Whiscash is extremely territorial. Just one of these Pokémon will claim a large pond as its exclusive territory. If a foe approaches it, it thrashes about and triggers a massive earthquake."	Whiskers Pokémon
WHISMUR	9	Whismur	"Normally, Whismur's voice is very quiet—it is barely audible even if one is paying close attention. However, if this Pokémon senses danger, it starts crying at an earsplitting volume."	Whisper Pokémon
WIGGLYTUFF	9	Wigglytuff	"Wigglytuff has large, saucerlike eyes. The surfaces of its eyes are always covered with a thin layer of tears. If any dust gets in this Pokémon's eyes, it is quickly washed away."	Balloon Pokémon
WINGULL	9	Wingull	Wingull has the habit of carrying prey and valuables in its beak and hiding them in all sorts of locations. This Pokémon rides the winds and flies as if it were skating across the sky.	Seagull Pokémon
WOBBUFFET	9	Wobbuffet	"If two or more Wobbuffet meet, they will turn competitive and try to outdo each other's endurance. However, they may try to see which one can endure the longest without food. Trainers need to beware of this habit."	Patient Pokémon
WOBBUFFET_PURIFIED_FORM	9	Wobbuffet	"If two or more Wobbuffet meet, they will turn competitive and try to outdo each other's endurance. However, they may try to see which one can endure the longest without food. Trainers need to beware of this habit."	Patient Pokémon
WOBBUFFET_SHADOW_FORM	9	Wobbuffet	"If two or more Wobbuffet meet, they will turn competitive and try to outdo each other's endurance. However, they may try to see which one can endure the longest without food. Trainers need to beware of this habit."	Patient Pokémon
WOOBAT	9	Woobat	The heart-shaped mark left on a body after a Woobat has been attached to it is said to bring good fortune.	Bat Pokémon
WOOPER	9	Wooper	"Wooper usually lives in water. However, it occasionally comes out onto land in search of food. On land, it coats its body with a gooey, toxic film."	Water Fish Pokémon
WORMADAM_PLANT_FORM	9	Wormadam	"When Burmy evolved, its cloak became a part of this Pokémon's body. The cloak is never shed."	Bagworm Pokémon
WORMADAM_SANDY_FORM	9	Wormadam	"When Burmy evolved, its cloak became a part of this Pokémon's body. The cloak is never shed."	Bagworm Pokémon
WORMADAM_TRASH_FORM	9	Wormadam	"When Burmy evolved, its cloak became a part of this Pokémon's body. The cloak is never shed."	Bagworm Pokémon
WURMPLE	9	Wurmple	"Using the spikes on its rear end, Wurmple peels the bark off trees and feeds on the sap that oozes out. This Pokémon's feet are tipped with suction pads that allow it to cling to glass without slipping."	Worm Pokémon
WYNAUT	9	Wynaut	"Wynaut can always be seen with a big, happy smile on its face. Look at its tail to determine if it is angry. When angered, this Pokémon will be slapping the ground with its tail."	Bright Pokémon
XATU	9	Xatu	Xatu stands rooted and still in one spot all day long. People believe that this Pokémon does so out of fear of the terrible things it has foreseen in the future.	Mystic Pokémon
YAMASK	9	Yamask	Each of them carries a mask that used to be its face when it was human. Sometimes they look at it and cry.	Spirit Pokémon
YAMASK_GALARIAN_FORM	9	Yamask	A clay slab with cursed engravings took possession of a Yamask. The slab is said to be absorbing the Yamask's dark power.	Spirit Pokémon
YANMA	9	Yanma	Yanma is capable of seeing 360 degrees without having to move its eyes. It is a great flier that is adept at making sudden stops and turning midair. This Pokémon uses its flying ability to quickly chase down targeted prey.	Clear Wing Pokémon
YANMEGA	9	Yanmega	This six-legged Pokémon is easily capable of transporting an adult in flight. The wings on its tail help it stay balanced.	Ogre Darner Pokémon
ZANGOOSE	9	Zangoose	Memories of battling its archrival Seviper are etched into every cell of Zangoose's body. This Pokémon adroitly dodges attacks with incredible agility.	Cat Ferret Pokémon
ZAPDOS	9	Zapdos	Zapdos is a Legendary Pokémon that has the ability to control electricity. It usually lives in thunderclouds. The Pokémon gains power if it is stricken by lightning bolts.	Electric Pokémon
ZEBSTRIKA	9	Zebstrika	"They have lightning-like movements. When Zebstrika run at full speed, the sound of thunder reverberates."	Thunderbolt Pokémon
ZEKROM	9	Zekrom	"Concealing itself in lightning clouds, it flies throughout the Unova region. It creates electricity in its tail."	Deep Black Pokémon
ZIGZAGOON	9	Zigzagoon	Zigzagoon restlessly wanders everywhere at all times. This Pokémon does so because it is very curious. It becomes interested in anything that it happens to see.	Tiny Raccoon Pokémon
ZIGZAGOON_GALARIAN_FORM	9	Zigzagoon	Zigzagoon restlessly wanders everywhere at all times. This Pokémon does so because it is very curious. It becomes interested in anything that it happens to see.	Tiny Raccoon Pokémon
ZOROARK	9	Zoroark	"If it thinks humans are going to discover its den, Zoroark shows them visions that make them wander around in the woods."	Illusion Fox Pokémon
ZORUA	9	Zorua	"If a normally talkative child suddenly stops talking, it may have been replaced by Zorua."	Tricky Fox Pokémon
ZUBAT	9	Zubat	Zubat remains quietly unmoving in a dark spot during the bright daylight hours. It does so because prolonged exposure to the sun causes its body to become slightly burned.	Bat Pokémon
ZUBAT_PURIFIED_FORM	9	Zubat	Zubat remains quietly unmoving in a dark spot during the bright daylight hours. It does so because prolonged exposure to the sun causes its body to become slightly burned.	Bat Pokémon
ZUBAT_SHADOW_FORM	9	Zubat	Zubat remains quietly unmoving in a dark spot during the bright daylight hours. It does so because prolonged exposure to the sun causes its body to become slightly burned.	Bat Pokémon
ZWEILOUS	9	Zweilous	"After it has eaten up all the food in its territory, it moves to another area. Its two heads do not get along."	Hostile Pokémon
CHESPIN	9	Chespin	"The quills on its head are usually soft. When it flexes them, the points become so hard and sharp that they can pierce rock."	"Spiny Nut Pokémon"
QUILLADIN	9	Quilladin	"It relies on its sturdy shell to deflect predators’ attacks. It counterattacks with its sharp quills."	"Spiny Armor Pokémon"
CHESNAUGHT	9	Chesnaught	"Its Tackle is forceful enough to flip a 50-ton tank. It shields its allies from danger with its own body."	"Spiny Armor Pokémon"
FENNEKIN	9	Fennekin	"Eating a twig fills it with energy, and its roomy ears give vent to air hotter than 390 degrees Fahrenheit."	"Fox Pokémon"
BRAIXEN	9	Braixen	"It has a twig stuck in its tail. With friction from its tail fur, it sets the twig on fire and launches into battle."	"Fox Pokémon"
DELPHOX	9	Delphox	"It gazes into the flame at the tip of its branch to achieve a focused state, which allows it to see into the future."	"Fox Pokémon"
FROAKIE	9	Froakie	"It secretes flexible bubbles from its chest and back. The bubbles reduce the damage it would otherwise take when attacked."	"Bubble Frog Pokémon"
FROGADIER	9	Frogadier	"It can throw bubble-covered pebbles with precise control, hitting empty cans up to a hundred feet away."	"Bubble Frog Pokémon"
GRENINJA	9	Greninja	"It creates throwing stars out of compressed water. When it spins them and throws them at high speed, these stars can split metal in two."	"Ninja Pokémon"
BUNNELBY	9	Bunnelby	"They use their large ears to dig burrows. They will dig the whole night through."	"Digging Pokémon"
DIGGERSBY	9	Diggersby	"With their powerful ears, they can heft boulders of a ton or more with ease. They can be a big help at construction sites."	"Digging Pokémon"
FLETCHLING	9	Fletchling	"These friendly Pokémon send signals to one another with beautiful chirps and tail-feather movements."	"Tiny Robin Pokémon"
FLETCHINDER	9	Fletchinder	"From its beak, it expels embers that set the tall grass on fire. Then it pounces on the bewildered prey that pop out of the grass."	"Ember Pokémon"
TALONFLAME	9	Talonflame	"In the fever of an exciting battle, it showers embers from the gaps between its feathers and takes to the air."	"Scorching Pokémon"
SCATTERBUG	9	Scatterbug	"When under attack from bird Pokémon, it spews a poisonous black powder that causes paralysis on contact."	"Scatterdust Pokémon"
SPEWPA	9	Spewpa	"It lives hidden within thicket shadows. When predators attack, it quickly bristles the fur covering its body in an effort to threaten them."	"Scatterdust Pokémon"
VIVILLON	9	Vivillon	"Vivillon with many different patterns are found all over the world. These patterns are affected by the climate of their habitat."	"Scale Pokémon"
LITLEO	9	Litleo	"The stronger the opponent it faces, the more heat surges from its mane and the more power flows through its body."	"Lion Cub Pokémon"
PYROAR	9	Pyroar	"The male with the largest mane of fire is the leader of the pride."	"Royal Pokémon"
FLABEBE	9	Flabebe	"It draws out and controls the hidden power of flowers. The flower Flabébé holds is most likely part of its body."	"Single Bloom Pokémon"
FLOETTE	9	Floette	"It flutters around fields of flowers and cares for flowers that are starting to wilt. It draws out the hidden power of flowers to battle."	"Single Bloom Pokémon"
FLORGES	9	Florges	"It claims exquisite flower gardens as its territory, and it obtains power from basking in the energy emitted by flowering plants."	"Garden Pokémon"
SKIDDO	9	Skiddo	"Thought to be one of the first Pokémon to live in harmony with humans, it has a placid disposition."	"Mount Pokémon"
GOGOAT	9	Gogoat	"It can tell how its Trainer is feeling by subtle shifts in the grip on its horns. This empathic sense lets them run as if one being."	"Mount Pokémon"
PANCHAM	9	Pancham	"It does its best to be taken seriously by its enemies, but its glare is not sufficiently intimidating. Chewing on a leaf is its trademark."	"Playful Pokémon"
PANGORO	9	Pangoro	"Although it possesses a violent temperament, it won’t put up with bullying. It uses the leaf in its mouth to sense the movements of its enemies."	"Daunting Pokémon"
FURFROU	9	Furfrou	"Trimming its fluffy fur not only makes it more elegant but also increases the swiftness of its movements."	"Poodle Pokémon"
ESPURR	9	Espurr	"The organ that emits its intense psychic power is sheltered by its ears to keep power from leaking out."	"Restraint Pokémon"
MEOWSTIC	9	Meowstic	"When in danger, it raises its ears and releases enough psychic power to grind a 10-ton truck into dust."	"Constraint Pokémon"
HONEDGE	9	Honedge	"Apparently this Pokémon is born when a departed spirit inhabits a sword. It attaches itself to people and drinks their life force."	"Sword Pokémon"
DOUBLADE	9	Doublade	"When Honedge evolves, it divides into two swords, which cooperate via telepathy to coordinate attacks and slash their enemies to ribbons."	"Sword Pokémon"
AEGISLASH	9	Aegislash	"Generations of kings were attended by these Pokémon, which used their spectral power to manipulate and control people and Pokémon."	"Royal Sword Pokémon"
SPRITZEE	9	Spritzee	"It emits a scent that enraptures those who smell it. This fragrance changes depending on what it has eaten."	"Perfume Pokémon"
AROMATISSE	9	Aromatisse	"It devises various scents, pleasant and unpleasant, and emits scents that its enemies dislike in order to gain an edge in battle."	"Fragrance Pokémon"
SWIRLIX	9	Swirlix	"To entangle its opponents in battle, it extrudes white threads as sweet and sticky as cotton candy."	"Cotton Candy Pokémon"
SLURPUFF	9	Slurpuff	"It can distinguish the faintest of scents. It puts its sensitive sense of smell to use by helping pastry chefs in their work."	"Meringue Pokémon"
INKAY	9	Inkay	"Opponents who stare at the flashing of the light-emitting spots on its body become dazed and lose their will to fight."	"Revolving Pokémon"
MALAMAR	9	Malamar	"It wields the most compelling hypnotic powers of any Pokémon, and it forces others to do whatever it wants."	"Overturning Pokémon"
BINACLE	9	Binacle	"Two Binacle live together on one rock. When they fight, one of them will move to a different rock."	"Two-Handed Pokémon"
BARBARACLE	9	Barbaracle	"When they evolve, two Binacle multiply into seven. They fight with the power of seven Binacle."	"Collective Pokémon"
SKRELP	9	Skrelp	"Camouflaged as rotten kelp, they spray liquid poison on prey that approaches unawares and then finish it off."	"Mock Kelp Pokémon"
DRAGALGE	9	Dragalge	"Their poison is strong enough to eat through the hull of a tanker, and they spit it indiscriminately at anything that enters their territory."	"Mock Kelp Pokémon"
CLAUNCHER	9	Clauncher	"They knock down flying prey by firing compressed water from their massive claws like shooting a pistol."	"Water Gun Pokémon"
CLAWITZER	9	Clawitzer	"Their enormous claws launch cannonballs of water powerful enough to pierce tanker hulls."	"Howitzer Pokémon"
HELIOPTILE	9	Helioptile	"They make their home in deserts. They can generate their energy from basking in the sun, so eating food is not a requirement."	"Generator Pokémon"
HELIOLISK	9	Heliolisk	"They flare their frills and generate energy. A single Heliolisk can generate sufficient electricity to power a skyscraper."	"Generator Pokémon"
SHIINOTIC	9	Shiinotic	\N	\N
SALANDIT	9	Salandit	\N	\N
TYRUNT	9	Tyrunt	"This Pokémon was restored from a fossil. If something happens that it doesn’t like, it throws a tantrum and runs wild."	"Royal Heir Pokémon"
TYRANTRUM	9	Tyrantrum	"The king of the ancient world, it can easily crunch a car with the devastating strength of its enormous jaws."	"Despot Pokémon"
AMAURA	9	Amaura	"This ancient Pokémon was restored from part of its body that had been frozen in ice for over 100 million years."	"Tundra Pokémon"
AURORUS	9	Aurorus	"The diamond-shaped crystals on its body expel air as cold as -240 degrees Fahrenheit, surrounding its enemies and encasing them in ice."	"Tundra Pokémon"
SYLVEON	9	Sylveon	"It sends a soothing aura from its ribbonlike feelers to calm fights."	"Intertwining Pokémon"
HAWLUCHA	9	Hawlucha	"Although its body is small, its proficient fighting skills enable it to keep up with big bruisers like Machamp and Hariyama."	"Wrestling Pokémon"
DEDENNE	9	Dedenne	"Its whiskers serve as antennas. By sending and receiving electrical waves, it can communicate with others over vast distances."	"Antenna Pokémon"
CARBINK	9	Carbink	"Born from the temperatures and pressures deep underground, it fires beams from the stone in its head."	"Jewel Pokémon"
GOOMY	9	Goomy	"The weakest Dragon-type Pokémon, it lives in damp, shady places, so its body doesn’t dry out."	"Soft Tissue Pokémon"
SLIGGOO	9	Sliggoo	"It drives away opponents by excreting a sticky liquid that can dissolve anything. Its eyes devolved, so it can’t see anything."	"Soft Tissue Pokémon"
GOODRA	9	Goodra	"This very friendly Dragon-type Pokémon will hug its beloved Trainer, leaving that Trainer covered in sticky slime."	"Dragon Pokémon"
KLEFKI	9	Klefki	"These key collectors threaten any attackers by fiercely jingling their keys at them."	"Key Ring Pokémon"
PHANTUMP	9	Phantump	"These Pokémon are created when spirits possess rotten tree stumps. They prefer to live in abandoned forests."	"Stump Pokémon"
TREVENANT	9	Trevenant	"It can control trees at will. It will trap people who harm the forest, so they can never leave."	"Elder Tree Pokémon"
PUMPKABOO	9	Pumpkaboo	"Small Pumpkaboo are said to be the product of areas where few lost souls lingered."	"Pumpkin Pokémon"
GOURGEIST	9	Gourgeist	"Singing in eerie voices, they wander town streets on the night of the new moon. Anyone who hears their song is cursed."	"Pumpkin Pokémon"
BERGMITE	9	Bergmite	"It blocks opponents’ attacks with the ice that shields its body. It uses cold air to repair any cracks with new ice."	"Ice Chunk Pokémon"
AVALUGG	9	Avalugg	"Its ice-covered body is as hard as steel. Its cumbersome frame crushes anything that stands in its way."	"Iceberg Pokémon"
NOIBAT	9	Noibat	"They live in pitch-black caves. Their enormous ears can emit ultrasonic waves of 200,000 hertz."	"Sound Wave Pokémon"
NOIVERN	9	Noivern	"They fly around on moonless nights and attack careless prey. Nothing can beat them in a battle in the dark."	"Sound Wave Pokémon"
XERNEAS	9	Xerneas	"Legends say it can share eternal life. It slept for a thousand years in the form of a tree before its revival."	"Life Pokémon"
YVELTAL	9	Yveltal	"When this legendary Pokémon’s wings and tail feathers spread wide and glow red, it absorbs the life force of living creatures."	"Destruction Pokémon"
SKWOVET	9	Skwovet	"It eats berries nonstop—a habit that has made it more resilient than it looks. It'll show up on farms, searching for yet more berries."	"Cheeky Pokémon"
GREEDENT	9	Greedent	"It stashes berries in its tail—so many berries that they fall out constantly. But this Pokémon is a bit slow-witted, so it doesn't notice the loss."	"Greedy Pokémon"
WOOLOO	9	Wooloo	"Its curly fleece is such an effective cushion that this Pokémon could fall off a cliff and stand right back up at the bottom, unharmed."	"Sheep Pokémon"
DUBWOOL	9	Dubwool	"Its majestic horns are meant only to impress the opposite gender. They never see use in battle."	"Sheep Pokémon"
FALINKS	9	Falinks	"Five of them are troopers, and one is the brass. The brass's orders are absolute."	"Formation Pokémon"
ZACIAN_HERO_FORM	9	Zacian	"Known as a legendary hero, this Pokémon absorbs metal particles, transforming them into a weapon it uses to battle."	"Warrior Pokémon"
ZACIAN_CROWNED_SWORD_FORM	9	Zacian	"Now armed with a weapon it used in ancient times, this Pokémon needs only a single strike to fell even Gigantamax Pokémon."	"Warrior Pokémon"
ZAMAZENTA_CROWNED_SHIELD_FORM	9	Zamazenta	"This Pokémon slept for aeons while in the form of a statue. It was asleep for so long, people forgot that it ever existed."	"Warrior Pokémon"
ZAMAZENTA_HERO_FORM	9	Zamazenta	"Now that it's equipped with its shield, it can shrug off impressive blows, including the attacks of Dynamax Pokémon."	"Warrior Pokémon"
ROWLET	9	Rowlet	\N	\N
DARTRIX	9	Dartrix	\N	\N
DECIDUEYE	9	Decidueye	\N	\N
LITTEN	9	Litten	\N	\N
TORRACAT	9	Torracat	\N	\N
INCINEROAR	9	Incineroar	\N	\N
POPPLIO	9	Popplio	\N	\N
BRIONNE	9	Brionne	\N	\N
PRIMARINA	9	Primarina	\N	\N
PIKIPEK	9	Pikipek	\N	\N
TRUMBEAK	9	Trumbeak	\N	\N
TOUCANNON	9	Toucannon	\N	\N
YUNGOOS	9	Yungoos	\N	\N
GUMSHOOS	9	Gumshoos	\N	\N
GRUBBIN	9	Grubbin	\N	\N
CHARJABUG	9	Charjabug	\N	\N
VIKAVOLT	9	Vikavolt	\N	\N
CRABRAWLER	9	Crabrawler	\N	\N
CRABOMINABLE	9	Crabominable	\N	\N
CUTIEFLY	9	Cutiefly	\N	\N
RIBOMBEE	9	Ribombee	\N	\N
ROCKRUFF	9	Rockruff	\N	\N
LYCANROC	9	Lycanroc	\N	\N
LYCANROC_MIDDAY_FORM	9	Lycanroc	\N	\N
LYCANROC_MIDNIGHT_FORM	9	Lycanroc	\N	\N
LYCANROC_DUSK_FORM	9	Lycanroc	\N	\N
WISHIWASHI	9	Wishiwashi	\N	\N
WISHIWASHI_SOLO_FORM	9	Wishiwashi	\N	\N
WISHIWASHI_SCHOOL_FORM	9	Wishiwashi	\N	\N
MAREANIE	9	Mareanie	\N	\N
TOXAPEX	9	Toxapex	\N	\N
MUDBRAY	9	Mudbray	\N	\N
MUDSDALE	9	Mudsdale	\N	\N
DEWPIDER	9	Dewpider	\N	\N
ARAQUANID	9	Araquanid	\N	\N
FOMANTIS	9	Fomantis	\N	\N
LURANTIS	9	Lurantis	\N	\N
MORELULL	9	Morelull	\N	\N
SILVALLY_ELECTRIC_FORM	9	Silvally	\N	\N
SILVALLY_FAIRY_FORM	9	Silvally	\N	\N
SILVALLY_FIGHTING_FORM	9	Silvally	\N	\N
SILVALLY_FIRE_FORM	9	Silvally	\N	\N
SILVALLY_FLYING_FORM	9	Silvally	\N	\N
SILVALLY_GHOST_FORM	9	Silvally	\N	\N
SILVALLY_GRASS_FORM	9	Silvally	\N	\N
SILVALLY_GROUND_FORM	9	Silvally	\N	\N
SILVALLY_ICE_FORM	9	Silvally	\N	\N
SILVALLY_POISON_FORM	9	Silvally	\N	\N
SILVALLY_PSYCHIC_FORM	9	Silvally	\N	\N
SILVALLY_ROCK_FORM	9	Silvally	\N	\N
SILVALLY_STEEL_FORM	9	Silvally	\N	\N
SILVALLY_WATER_FORM	9	Silvally	\N	\N
MINIOR	9	Minior	\N	\N
MINIOR_METEOR_FORM	9	Minior	\N	\N
MINIOR_BLUE_FORM	9	Minior	\N	\N
MINIOR_GREEN_FORM	9	Minior	\N	\N
MINIOR_INDIGO_FORM	9	Minior	\N	\N
MINIOR_ORANGE_FORM	9	Minior	\N	\N
MINIOR_RED_FORM	9	Minior	\N	\N
MINIOR_VIOLET_FORM	9	Minior	\N	\N
MINIOR_YELLOW_FORM	9	Minior	\N	\N
KOMALA	9	Komala	\N	\N
TURTONATOR	9	Turtonator	\N	\N
TOGEDEMARU	9	Togedemaru	\N	\N
MIMIKYU	9	Mimikyu	\N	\N
MIMIKYU_BUSTED_FORM	9	Mimikyu	\N	\N
MIMIKYU_DISGUISED_FORM	9	Mimikyu	\N	\N
BRUXISH	9	Bruxish	\N	\N
DRAMPA	9	Drampa	\N	\N
DHELMISE	9	Dhelmise	\N	\N
JANGMO_O	9	Jangmo-o	\N	\N
HAKAMO_O	9	Hakamo-o	\N	\N
KOMMO_O	9	Kommo-o	\N	\N
TAPU_KOKO	9	Tapu Koko	\N	\N
TAPU_LELE	9	Tapu Lele	\N	\N
TAPU_BULU	9	Tapu Bulu	\N	\N
TAPU_FINI	9	Tapu Fini	\N	\N
COSMOG	9	Cosmog	\N	\N
COSMOEM	9	Cosmoem	\N	\N
SOLGALEO	9	Solgaleo	\N	\N
LUNALA	9	Lunala	\N	\N
NIHILEGO	9	Nihilego	\N	\N
BUZZWOLE	9	Buzzwole	\N	\N
PHEROMOSA	9	Pheromosa	\N	\N
XURKITREE	9	Xurkitree	\N	\N
CELESTEELA	9	Celesteela	\N	\N
KARTANA	9	Kartana	\N	\N
GUZZLORD	9	Guzzlord	\N	\N
NECROZMA	9	Necrozma	\N	\N
NECROZMA_DUSK_MANE_FORM	9	Necrozma	\N	\N
NECROZMA_DAWN_WINGS_FORM	9	Necrozma	\N	\N
NECROZMA_ULTRA_FORM	9	Necrozma	\N	\N
MAGEARNA	9	Magearna	\N	\N
MAGEARNA_ORIGINAL_COLOR_FORM	9	Magearna	\N	\N
MARSHADOW	9	Marshadow	\N	\N
POIPOLE	9	Poipole	\N	\N
NAGANADEL	9	Naganadel	\N	\N
STAKATAKA	9	Stakataka	\N	\N
BLACEPHALON	9	Blacephalon	\N	\N
ZERAORA	9	Zeraora	\N	\N
\.


-- Completed on 2023-08-29 10:03:02

--
-- PostgreSQL database dump complete
--

