"""Shorter English for strings that would otherwise be shrunk a lot to fit their box (center banners below
about 63%, other text below about 72%). Keyed on the English with its line breaks joined and without the
battle message tag (official PS3 text, or the DLC translation in text/dlc); applied by build_text.english
to the base game and the DLC. Placeholders and color tags are kept; the result is wrapped/shrunk as usual."""

SHORT = {
    # center banners (battle messages, orders: also the mission panel objective)
    "[0:CHARA_G] is advancing towards [2:FLD] again due to the [r]enemy forces'[/] destruction!":
        '[r]Enemy forces[/] down! [0:CHARA_G] heads for [2:FLD] again!',
    'The [r]bombardment[/] of [2:FLD] stopped due to the withdrawal of [0:MS_G]!':
        '[0:MS_G] withdrew! [2:FLD] [r]bombardment[/] ends!',
    '[0:MS_G] is approaching [2:FLD_PRE]! Do not let it reach [2:FLD_PRE]!':
        '[0:MS_G] is nearing [2:FLD_PRE]! Stop it!',
    "[0:CHARA_G] has withdrawn from the battlefield due to the destruction of [1:CHARA_G]'s forces!":
        "[1:CHARA_G]'s forces destroyed! [0:CHARA_G] has withdrawn!",
    '[r]ZAFT forces[/] have deployed [2:FLD_PRE]! Unable to escape from [2:FLD_PRE]!':
        '[r]ZAFT forces[/] deployed [2:FLD_PRE]! There is no escape!',
    '[b]Alliance forces[/] were unable to reach the battlefield due to the interference from [r]ZAFT forces[/]!':
        '[r]ZAFT forces[/] kept the [b]Alliance forces[/] from reaching the battle!',
    "[0:CHARA_G] and [1:CHARA_G] are advancing to break through the [r]Orb forces' defense point[/]!":
        '[0:CHARA_G] and [1:CHARA_G] advance on the [r]Orb defense point[/]!',
    '[r]Enemy reinforcements[/] have appeared, and are targeting the withdrawing [b]Federation forces[/]!':
        '[r]Enemy reinforcements[/] target the withdrawing [b]Federation forces[/]!',
    'It seems they will rendezvous with the concealed [r]enemy detachment[/] at [2:FLD]!':
        'They plan to meet a hidden [r]enemy detachment[/] at [2:FLD]!',
    '[0:MS_G] has deployed an [r]interception force commander[/] to assist [1:CHARA_G]!':
        '[0:MS_G] sent an [r]interceptor commander[/] to aid [1:CHARA_G]!',
    'The [r]enemy[/] field commanders [0:CHARA_G] and [1:CHARA_G] have launched! Destroy them!':
        '[r]Enemy[/] leaders [0:CHARA_G] and [1:CHARA_G] launch! Destroy them!',
    '[0:MS_G] stopped [b]bombarding the enemy[/] due to the capture of [b]defense points[/]!':
        '[b]Defense points[/] taken! [0:MS_G] stops firing!',
    "[0:CHARA_G]'s forces are unable to head out, as [r]enemy forces[/] have stolen their [g]medicine[/]!":
        "[r]Enemy forces[/] stole the [g]medicine[/]! [0:CHARA_G]'s forces can't move out!",
    'More [r]enemy combat engineers[/] have appeared! They are assaulting [0:MS_G]!':
        'More [r]enemy engineers[/]! They are assaulting [0:MS_G]!',
    "[0:CHARA_G] was unsettled by the [r]enemy combat engineers'[/] manipulation of information!":
        "[0:CHARA_G] is shaken by the [r]enemy engineers'[/] disinformation!",
    'Successfully sank [0:MS_G]! [0:MS_G] has temporarily withdrawn!':
        '[0:MS_G] sunk! It has temporarily withdrawn!',
    '[2:FLD_PRE] and [3:FLD_PRE] have fallen to [0:CHARA_G] and the others!':
        "[0:CHARA_G]'s group took [2:FLD_PRE] and [3:FLD_PRE]!",
    "[0:CHARA_G]'s forces have stopped advancing due to the interference of [r]enemy forces[/]!":
        "[r]Enemy forces[/] have halted [0:CHARA_G]'s advance!",
    'Destroy the [r]enemy forces[/] before the self-destruct activates, and rescue [0:CHARA_G]!':
        'Beat the [r]enemy[/] and save [0:CHARA_G] before the self-destruct!',
    'The [y]Earth Federation Forces[/] have sensed the fighting and are approaching! Watch out!':
        'The [y]Federation Forces[/] sensed the fighting and are coming! Watch out!',
    '[0:CHARA_G] has withdrawn from the battlefield to pursue the [r]enemy transport forces[/]!':
        '[0:CHARA_G] withdrew to pursue the [r]enemy transports[/]!',
    'Capture [2:FLD_PRE] and [3:FLD_PRE], and break the [r]enemy[/] formation!':
        'Take [2:FLD_PRE] and [3:FLD_PRE]! Break the [r]enemy[/]!',
    "[0:MS_G] has stopped advancing due to [2:FLD]'s interference!":
        '[2:FLD] has halted [0:MS_G]!',
    'Approaching the [g]atmosphere[/]! Watch the time remaining until entering the [g]atmosphere[/]!':
        'Nearing the [g]atmosphere[/]! Watch the time left until entry!',
    '[0:CHARA_G] is advancing towards [2:FLD], where [1:CHARA_G] is located.':
        '[0:CHARA_G] heads for [1:CHARA_G] at [2:FLD].',
    '[0:CHARA_G] and the others leave the battlefield to engage the [r]enemy reinforcements[/]!':
        '[0:CHARA_G] and the others leave to engage [r]enemy reinforcements[/]!',
    '[r]Enemy forces[/] have appeared outside the [g]fortress[/]! They are advancing the [b]allied fleet[/]!':
        '[r]Enemy forces[/] outside the [g]fortress[/]! They advance on the [b]allied fleet[/]!',
    '[0:MS_G] was shot down! [0:CHARA_G] has withdrawn from the battlefield!':
        '[0:MS_G] shot down! [0:CHARA_G] has withdrawn!',
    '[0:CHARA_G] has stopped advancing due to the interference of [r]enemy assault forces[/]!':
        '[r]Enemy assault forces[/] have halted [0:CHARA_G]!',
    '[0:CHARA_G] has appeared outside [g]Palau[/]! [b]Federation forces[/] are moving to intercept!':
        '[0:CHARA_G] outside [g]Palau[/]! [b]Federation forces[/] move to intercept!',
    '[2:FLD] captured! Successfully prevented [0:CHARA_G] from appearing!':
        '[2:FLD] captured! [0:CHARA_G] can no longer appear!',
    '[r]Enemy forces[/] have appeared! They launch a surprise attack on [0:MS_G]!':
        '[r]Enemy forces[/]! A surprise attack on [0:MS_G]!',
    'With [2:FLD_PRE] fallen, [0:CHARA_G] and [1:CHARA_G] temporarily withdraw!':
        '[2:FLD_PRE] fell! [0:CHARA_G] and [1:CHARA_G] withdraw!',
    '[1:CHARA_G] has appeared from [2:FLD] and [3:FLD] again!':
        '[1:CHARA_G] is back at [2:FLD] and [3:FLD]!',
    '[r]Enemy forces[/] have appeared outside [g]Palau[/], and are attacking the [b]Federation forces[/]!':
        '[r]Enemy forces[/] outside [g]Palau[/] attack the [b]Federation forces[/]!',
    'Shoot down the approaching [r]enemy forces[/] and push back the [r]enemy protective line[/]!':
        'Shoot down the [r]enemy forces[/] and push back the [r]enemy line[/]!',
    "[0:CHARA_G]'s machine was wrecked by [1:CHARA_G]'s attacks, and has withdrawn!":
        "[1:CHARA_G] wrecked [0:CHARA_G]'s machine! It has withdrawn!",
    '[0:CHARA_G] is furious that they were not able to deal the final blow to [1:CHARA_G]!':
        '[0:CHARA_G] is furious at failing to finish off [1:CHARA_G]!',
    '[0:MS_G] has engaged in battle with [1:CHARA_G] as it tries to withdraw!':
        '[0:MS_G] fights [1:CHARA_G] while withdrawing!',
    '[0:CHARA_G] has arrived at [2:FLD] and withdrawn from the battlefield!':
        '[0:CHARA_G] reached [2:FLD] and has withdrawn!',
    "[0:MS_G] has been destroyed! [b]Mu La Flaga[/]'s machine has been wrecked!":
        "[0:MS_G] destroyed! [b]Mu La Flaga[/]'s machine is wrecked!",
    'The [b]allied escort[/] has been wiped out! The operation cannot continue. Mission failed!':
        'The [b]allied escort[/] was wiped out! Mission failed!',
    '[b]Defense force[/] has appeared! They are searching for the [r]enemy[/] that set the [g]bomb[/]!':
        '[b]Defense force[/] here! They hunt the [r]enemy[/] who set the [g]bomb[/]!',
    '[r]Enemy reinforcements[/] have appeared after noticing something amiss in the [g]colony[/]!':
        'Sensing trouble in the [g]colony[/], [r]enemy reinforcements[/] appear!',
    'Failed to sink [0:MS_G]! [0:MS_G] has temporarily withdrawn!':
        'Failed to sink [0:MS_G]! It has temporarily withdrawn!',
    'Unable to enter [2:FLD] as it is under the control of the [y]Alliance forces[/]!':
        "[2:FLD] is held by the [y]Alliance forces[/]! Can't enter!",
    'With the [b]Gato Unit[/] withdrawing, the defense of [2:FLD] has weakened!':
        'The [b]Gato Unit[/] withdrew! [2:FLD] is now weakly defended!',
    'The [g]colony[/] has passed the point of no return! It seems set to fall on North America!':
        'The [g]colony[/] is past the point of no return! It will hit North America!',
    '[0:MS_G] begins a [r]bombardment[/] targeting [1:CHARA_G] and the others!':
        '[0:MS_G] begins [r]bombarding[/] [1:CHARA_G] and the others!',
    '[0:CHARA_G] has been surrounded at [2:FLD], and is unable to escape!':
        '[0:CHARA_G] is trapped at [2:FLD]!',
    '[b]Federation forces[/] and [r]Zeon forces[/] have withdrawn from the collapsing [g]A Baoa Qu[/]!':
        '[b]Federation[/] and [r]Zeon forces[/] flee the collapsing [g]A Baoa Qu[/]!',
    "[0:CHARA_G] and [1:CHARA_G] 's will to fight has increased after their rendezvous!":
        '[0:CHARA_G] and [1:CHARA_G] regrouped! Their morale rises!',
    "[0:CHARA_G] has withdrawn from the battlefield to head to [1:CHARA_G]'s location!":
        '[0:CHARA_G] has withdrawn to join [1:CHARA_G]!',
    "Drive off the [y]Earth Federation Forces[/] and cover [0:MS_G]'s withdrawal!":
        "Drive off the [y]Federation Forces[/] and cover [0:MS_G]'s retreat!",
    'More [r]enemy fields[/] have appeared! They are blocking the advance of [0:CHARA_G]!':
        "More [r]enemy fields[/]! They block [0:CHARA_G]'s advance!",
    'More [0:CHARA_G] reinforcements have appeared! They advance on [1:CHARA_G]!':
        'More [0:CHARA_G] reinforcements! They advance on [1:CHARA_G]!',
    'Rendezvous with [1:CHARA_G], who is engaged in battle with [0:MS_G]!':
        'Join [1:CHARA_G] in the battle with [0:MS_G]!',
    '[0:CHARA_G] and [1:CHARA_G] have temporarily withdrawn to protect [b]White Base[/]!':
        '[0:CHARA_G] and [1:CHARA_G] withdrew to guard [b]White Base[/]!',
    '[0:MS_G] has gone on the offensive and can now enter the [r]enemy field[/]!':
        '[0:MS_G] attacks! It can now enter the [r]enemy field[/]!',
    "[0:CHARA_G]'s forces have escaped [g]Palau[/] from another route to pursue to enemy!":
        "[0:CHARA_G]'s forces left [g]Palau[/] by another route to give chase!",
    '[r]Enemy scout forces[/] wiped out! Successfully prevented the [r]enemy[/] [g]gathering intel[/]!':
        '[r]Enemy scouts[/] wiped out! The [r]enemy[/] [g]gathered no intel[/]!',
    '[0:CHARA_G] and the others break off their alliance to decide the strongest "[r]Red[/]"!':
        '[0:CHARA_G] and the others split to decide the strongest "[r]Red[/]"!',
    'Now able to enter [3:FLD] due to the capture of [2:FLD]!':
        '[2:FLD] captured! [3:FLD] is now open!',
    "[0:CHARA_G] has temporarily withdrawn after detecting [1:CHARA_G]'s presence!":
        '[0:CHARA_G] sensed [1:CHARA_G] and withdrew for now!',
    'You can now advance into the [r]enemy field[/] where [0:CHARA_G] and the others are!':
        'The [r]enemy field[/] of [0:CHARA_G] and the others is now open!',
    "[0:CHARA_G]'s forces have withdrawn due to the damage to [0:MS_G]!":
        "[0:MS_G] damaged! [0:CHARA_G]'s forces withdrew!",
    '[0:CHARA_G] prepares to withdraw to keep [0:MS_G] from being sunk!':
        '[0:CHARA_G] withdraws to save [0:MS_G]!',
    'The way into [2:FLD] is closed! Unable to enter [2:FLD]!':
        'The way into [2:FLD] is closed!',
    '[0:CHARA_G] has stopped advancing due to the interference of the [r]AEUG forces[/]!':
        'The [r]AEUG forces[/] have halted [0:CHARA_G]!',
    'More [r]Federation reinforcements[/] have appeared! They advance into the [g]fortress[/]!':
        'More [r]Federation reinforcements[/] advance into the [g]fortress[/]!',
    'More [r]Federation reinforcements[/] advance, targeting [0:CHARA_G] and the others!':
        'More [r]Federation reinforcements[/] target [0:CHARA_G] and the others!',
    '[0:CHARA_G] has engaged in battle with [1:CHARA_G] outside the battle airspace.':
        '[0:CHARA_G] fights [1:CHARA_G] outside the battle airspace.',
    'Now able to enter [2:FLD], as [r]enemy forces[/] are no longer blocking it!':
        '[r]Enemy forces[/] gone! [2:FLD] is now open!',
    '[0:CHARA_G] and the others have appeared to help capture [2:FLD]!':
        '[0:CHARA_G] and the others arrive to help take [2:FLD]!',
    '[0:FLD_ALGO] is in imminent danger! Provide immediate assistance!':
        '[0:FLD_ALGO] is in danger! Assist at once!',
    '[r]Musai[/] preparing to fire! Do not allow the [b]allied battleships[/] to be destroyed!':
        '[r]Musai[/] preparing to fire! Protect the [b]allied battleships[/]!',
    '[r]Enemy reinforcements[/] have appeared, and are advancing on the [b]White Base[/]!':
        '[r]Enemy reinforcements[/] advance on the [b]White Base[/]!',
    '[r]Enemy combat engineers[/] surrounded [2:FLD] in the confusion!':
        '[r]Enemy engineers[/] surrounded [2:FLD]!',
    '[0:CHARA_G] has withdrawn from the battlefield after completing the mission!':
        '[0:CHARA_G] completed the mission and withdrew!',
    'The crew of [b]White Base[/] are fighting at close quarters inside the [g]fortress[/]!':
        'The [b]White Base[/] crew fight inside the [g]fortress[/]!',
    'The [r]Solar System[/] has been activated! Move away from its line of fire quickly!':
        'The [r]Solar System[/] is active! Leave its line of fire!',
    'Unable to enter [2:FLD] due to the interference of [r]Enemy forces[/]!':
        '[r]Enemy forces[/] block the way into [2:FLD]!',
    'Destroy the [r]enemy forces[/] and break through the [g]Gryps 2[/] line of defense!':
        'Destroy the [r]enemy[/] and break the [g]Gryps 2[/] defenses!',
    '[b]Axis forces[/] stopping advancing after seeing the [b]AEUG[/] struggle in battle!':
        'Seeing the [b]AEUG[/] struggle, [b]Axis forces[/] halt!',
    'Destroy the [r]enemy defense force[/] and advance towards [2:FLD]!':
        'Destroy the [r]defenders[/] and advance on [2:FLD]!',
    '[0:MS_G] was damaged by an attack from an [r]unknown enemy[/]!':
        'An [r]unknown enemy[/] damaged [0:MS_G]!',
    "[0:CHARA_G]'s reinforcements stopped due to the fall of [2:FLD]!":
        "[2:FLD] fell! [0:CHARA_G]'s reinforcements stop!",
    '[2:FLD] was weakened by the shooting down of [0:CHARA_G]!':
        '[0:CHARA_G] down! [2:FLD] is weakened!',
    '[0:CHARA_G] has withdrawn from the battlefield in pursuit of [1:CHARA_G]!':
        '[0:CHARA_G] withdrew to pursue [1:CHARA_G]!',
    'The [b]Ra Cailum[/] is approaching the battlefield with [g]nuclear missiles[/] on board!':
        'The [b]Ra Cailum[/] approaches with [g]nuclear missiles[/]!',
    'The [r]bombardment[/] stopped due to the destruction of [0:MS_G]!':
        '[0:MS_G] destroyed! The [r]bombardment[/] stops!',
    'Destroy [0:MS_G] quickly before it reaches the [g]missile launch point[/]!':
        'Destroy [0:MS_G] before it reaches the [g]launch point[/]!',
    'Keep an eye on the [g]time limit[/], and do not allow [0:CHARA_G] to be shot down!':
        'Watch the [g]time limit[/] and protect [0:CHARA_G]!',
    "The [b]Axis interior[/] has taken extensive damage from [0:CHARA_G]'s attacks!":
        '[0:CHARA_G] has badly damaged the [b]Axis interior[/]!',
    '[b]Mu La Flaga[/] of the [b]Earth Alliance forces[/] has rendezvoused with the [b]Archangel[/]!':
        '[b]Mu La Flaga[/] has joined the [b]Archangel[/]!',
    'Now able to enter [2:FLD] due to the destruction of [0:CHARA_G]!':
        '[0:CHARA_G] destroyed! [2:FLD] is open!',
    'Capture [2:FLD_PRE] quickly and rendezvous with [0:MS_G]!':
        'Take [2:FLD_PRE] and join [0:MS_G]!',
    'Launching an all-out attack on [2:FLD] and [0:MS_G]!':
        'All-out attack on [2:FLD] and [0:MS_G]!',
    '[0:CHARA_G] and [1:CHARA_G] have temporarily withdrawn from the [g]colony[/]!':
        '[0:CHARA_G] and [1:CHARA_G] left the [g]colony[/] for now!',
    '[0:MS_G] has stopped advancing due to [r]enemy reinforcements[/]!':
        '[r]Enemy reinforcements[/] halt [0:MS_G]!',
    '[0:CHARA_G] protected [1:CHARA_G]! They were taken on board the [b]Minerva[/]!':
        '[0:CHARA_G] saved [1:CHARA_G]! Both board the [b]Minerva[/]!',
    'The [r]main Earth force[/] and [r]Orb reinforcements[/] have appeared on the battlefield!':
        'The [r]Earth main force[/] and [r]Orb reinforcements[/] appear!',
    '[0:CHARA_G] moved through the water and reappeared at [2:FLD]!':
        '[0:CHARA_G] came through the water to [2:FLD]!',
    'Now able to enter [2:FLD] due to [0:CHARA_G] being shot down!':
        '[0:CHARA_G] down! [2:FLD] is open!',
    'Shoot down [0:CHARA_G] and [1:CHARA_G] quickly before you are outflanked!':
        'Down [0:CHARA_G] and [1:CHARA_G] before you are flanked!',
    '[0:CHARA_G] is unable to maneuver due to the capture of the [r]enemy field[/]!':
        '[r]Enemy field[/] taken! [0:CHARA_G] is pinned!',
    'Keep an eye on [g]how much time is left[/] before [0:MS_G] withdraws!':
        'Watch the [g]time left[/] before [0:MS_G] withdraws!',
    "[2:FLD] has disappeared due to [0:CHARA_G]'s being shot down!":
        '[0:CHARA_G] down! [2:FLD] is gone!',
    '[0:MS_G] stopped its [r]bombardment[/] in preparation for withdraw!':
        '[0:MS_G] stops its [r]bombardment[/] to withdraw!',
    '[0:CHARA_G] can enter the [r]enemy field[/] due to the advance of [1:CHARA_G]!':
        "[1:CHARA_G]'s advance lets [0:CHARA_G] enter the [r]enemy field[/]!",
    '[0:CHARA_G] is beginning to lay down [b]beam support fire[/] on [1:MS_G]!':
        '[0:CHARA_G] gives [b]beam support[/] to [1:MS_G]!',
    'Shoot down [0:CHARA_G] and secure the [g]arrival point[/] for the [b]Alliance forces[/]!':
        'Down [0:CHARA_G] and secure the [b]Alliance[/] [g]landing point[/]!',
    '[r]Zinnerman[/] ordered [0:CHARA_G] to make an attack to cover the withdrawal!':
        '[r]Zinnerman[/] orders [0:CHARA_G] to cover the retreat!',
    'Capture the [r]enemy fields[/] and cover the withdrawal of the [b]Federation forces[/]!':
        'Take the [r]enemy fields[/] and cover the [b]Federation[/] retreat!',
    "Unable to escape [2:FLD] due to [0:CHARA_G]'s interference!":
        '[0:CHARA_G] blocks escape from [2:FLD]!',
    'Sink [0:MS_G] quickly and prevent [1:CHARA_G] from appearing!':
        'Sink [0:MS_G] before [1:CHARA_G] appears!',
    "[0:CHARA_G]'s [g]Federation forces[/] have not joined the battle, and are on standby!":
        "[0:CHARA_G]'s [g]Federation forces[/] stand by!",
    '[1:CHARA_G] have appeared from the [r]enemy fields[/] around [0:MS_G]!':
        '[1:CHARA_G] emerge from [r]enemy fields[/] near [0:MS_G]!',
    'Destroy the [r]enemy forces[/] and assist the withdrawal of the [b]Federation forces[/]!':
        'Destroy the [r]enemy[/] and cover the [b]Federation[/] retreat!',
    '[r]Enemy interception forces[/] have appeared, and are advancing on [0:CHARA_G]!':
        '[r]Enemy interceptors[/] advance on [0:CHARA_G]!',
    'An [r]enemy assault commander[/] has appeared, and is targeting [b]Federation forces[/]!':
        'An [r]enemy assault commander[/] targets the [b]Federation[/]!',
    '[r]Federation forces[/] have closed the [g]gate[/] to cover the withdrawal of [0:CHARA_G]!':
        'The [r]Federation[/] shut the [g]gate[/] to cover [0:CHARA_G]!',
    "[0:CHARA_G]'s forces have appeared in the path of [1:CHARA_G]'s withdrawal!":
        "[0:CHARA_G]'s forces block [1:CHARA_G]'s retreat!",
    'Shoot down [0:CHARA_G] quickly to stop them reaching [2:FLD]!':
        'Down [0:CHARA_G] before they reach [2:FLD]!',
    'It seems they will withdraw from the battlefield as soon as [0:CHARA_G] arrives!':
        'They will withdraw once [0:CHARA_G] arrives!',
    '[0:CHARA_G] is approaching the battlefield to capture [1:MS_G]!':
        '[0:CHARA_G] approaches to capture [1:MS_G]!',
    '[0:CHARA_G] has stopped advancing after being attacked by [r]Federation forces[/]!':
        '[r]Federation forces[/] attack and halt [0:CHARA_G]!',
    '[0:CHARA_G] stopped advancing due to the interference of [r]enemy forces[/]!':
        '[r]Enemy forces[/] have halted [0:CHARA_G]!',
    'Destroy the [r]fleeing enemy forces[/] before they reach [2:FLD]!':
        'Destroy the [r]fleeing enemy[/] before [2:FLD]!',
    'The [g]time limit[/] is up, and you are unable to continue combat! You lost the battle!':
        "[g]Time's up[/]! You can't fight on! Battle lost!",
    'The [r]enemy[/] field commanders [0:CHARA_G] and [1:CHARA_G] have appeared!':
        '[r]Enemy[/] commanders [0:CHARA_G] and [1:CHARA_G] appear!',
    'Destroy the [r]enemy ambush force[/] before they reach [2:FLD]!':
        'Destroy the [r]ambush force[/] before [2:FLD]!',
    '[r]Enemy transport forces[/] have appeared, and are heading to the [r]destination[/]!':
        '[r]Enemy transports[/] head for their [r]destination[/]!',
    'Destroy [0:CHARA_G] and prevent [r]enemy reinforcements[/] from appearing!':
        'Destroy [0:CHARA_G] to stop [r]enemy reinforcements[/]!',
    'Shoot down [0:CHARA_G] quickly to prevent [y]enemy reinforcements[/] appearing!':
        'Down [0:CHARA_G] fast to stop [y]enemy reinforcements[/]!',
    '[0:CHARA_G] has evaded the [r]enemy[/] attacks and withdrawn from the battlefield!':
        '[0:CHARA_G] evaded the [r]enemy[/] and withdrew!',
    '[0:CHARA_G] has fulfilled their objective, and withdrawn with [1:CHARA_G]!':
        '[0:CHARA_G] is done and withdraws with [1:CHARA_G]!',
    'This does not seem to be one of the [b]allies[/] that [0:CHARA_G] was searching for!':
        'Not one of the [b]allies[/] [0:CHARA_G] was seeking!',
    '[0:CHARA_G] and [1:CHARA_G] have appeared, and are engaged in combat!':
        '[0:CHARA_G] and [1:CHARA_G] appear and clash!',
    'Destroy the [r]enemy transport forces[/] before they reach [2:FLD]!':
        'Destroy the [r]transports[/] before [2:FLD]!',
    '[r]Enemy transport forces[/] have reached [2:FLD] and withdrawn!':
        '[r]Enemy transports[/] reached [2:FLD] and left!',
    "[0:CHARA_G] has appeared on the battlefield, seeking [1:CHARA_G]'s parts!":
        "[0:CHARA_G] appears, seeking [1:CHARA_G]'s parts!",
    '[0:CHARA_G] has withdrawn from the battlefield to seek a worthy opponent!':
        '[0:CHARA_G] withdrew to seek a worthy foe!',
    'Destroy the [r]enemy attackers[/] while assisting [0:CHARA_G] and the others!':
        'Destroy the [r]attackers[/] and help [0:CHARA_G]!',
    'Escort [0:CHARA_G] to [2:FLD], where [1:CHARA_G] is located.':
        'Escort [0:CHARA_G] to [1:CHARA_G] at [2:FLD].',
    "[1:CHARA_G] is advancing again due to the destruction of [0:CHARA_G]'s forces!":
        "[0:CHARA_G]'s forces destroyed! [1:CHARA_G] advances!",
    'Successfully prevented the rendezvous of [0:CHARA_G] and [1:CHARA_G]!':
        'Stopped [0:CHARA_G] and [1:CHARA_G] from meeting!',
    'Destroy [0:CHARA_G] or [1:CHARA_G] before they reach [2:FLD]!':
        'Stop [0:CHARA_G] or [1:CHARA_G] before [2:FLD]!',
    '[0:CHARA_G] and [1:CHARA_G] are withdrawing after achieving their objectives!':
        '[0:CHARA_G] and [1:CHARA_G] are done and withdraw!',
    'Destroy the [r]nuclear attack forces[/] before they reach [2:FLD]!':
        'Destroy the [r]nuclear force[/] before [2:FLD]!',
    'Shoot down the [r]enemy forces[/] carrying the [g]medicine[/] before the [g]time limit[/] is up!':
        'Down the [r]enemy[/] with the [g]medicine[/] in [g]time[/]!',
    "[0:CHARA_G] will not launch, due to [1:CHARA_G]'s team having been shot down.":
        "[1:CHARA_G]'s team is down. [0:CHARA_G] won't launch.",
    'Destroy the one whose mother was involved in developing the [g]Gundam F91[/]!':
        'Destroy the one whose mother built the [g]Gundam F91[/]!',
    'The [r]enemy sabotage units[/] begin work to surround [0:CHARA_G] and the others!':
        '[r]Saboteurs[/] begin to surround [0:CHARA_G] and the others!',
    '[0:CHARA_G] and the others have appeared to defend [2:FLD]!':
        '[0:CHARA_G] and others arrive to defend [2:FLD]!',
    '[r]Enemy[/] resistance at [2:FLD] has weakened! It can be entered!':
        '[r]Enemy[/] resistance at [2:FLD] weakens! Enter now!',
    '[0:CHARA_G] has finished repairs and launches from [1:MS_G]!':
        '[0:CHARA_G] is repaired and launches from [1:MS_G]!',
    '[b]All forces[/] begin to withdraw before the [r]Federation Forces[/] resume their attack!':
        '[b]All forces[/] withdraw before the [r]Federation[/] strikes again!',
    'Taking advantage of the [b]Zeon[/] confusion, [r]Federation reinforcements[/] appear!':
        'Amid [b]Zeon[/] confusion, [r]Federation reinforcements[/] appear!',
    '[0:CHARA_G] and [1:CHARA_G] appear on the battlefield with [r]reinforcements[/]!':
        '[0:CHARA_G] and [1:CHARA_G] arrive with [r]reinforcements[/]!',
    'Held up at [2:FLD], [0:MS_G] has stopped moving!':
        '[0:MS_G] is stuck at [2:FLD]!',
    '[0:CHARA_G] has broken through [2:FLD] and is moving again!':
        '[0:CHARA_G] broke through [2:FLD]!',
    "[2:FLD] was destroyed by [0:MS_G]'s suicide charge!":
        "[0:MS_G]'s suicide charge destroyed [2:FLD]!",
    'Defeat [0:CHARA_G] and cover the withdrawal of [1:CHARA_G] and the others!':
        "Defeat [0:CHARA_G] and cover [1:CHARA_G]'s retreat!",
    'You covered the withdrawal of [0:MS_G] and [1:MS_G]!':
        '[0:MS_G] and [1:MS_G] got away safely!',
    'Defeat [0:CHARA_G] and [1:CHARA_G] and hold the colony laser at all costs!':
        'Defeat [0:CHARA_G] and [1:CHARA_G]! Hold the colony laser!',
    "[0:CHARA_G]'s machine was damaged fighting [1:CHARA_G]! Support at once!":
        '[1:CHARA_G] damaged [0:CHARA_G]! Support at once!',
    'The [g]time limit[/] ran out and the sabotage could not be stopped! Mission failed!':
        "[g]Time's up[/]! The sabotage succeeded! Mission failed!",
    'The [r]Jupiter Empire[/] begins fighting back against the [b]Crossbone Vanguard[/]!':
        'The [r]Jupiter Empire[/] strikes back at the [b]Crossbone Vanguard[/]!',
    'The [y]Earth Federation Forces[/] appear to be launching [0:MS_G]!':
        'The [y]Federation Forces[/] are launching [0:MS_G]!',
    "Defeat the [r]Zeon remnants[/]' fleet and break through the [r]enemy defense line[/]!":
        'Defeat the [r]Zeon remnant[/] fleet and break their [r]line[/]!',
    'The [r]Axis forces[/] appear on the battlefield to collect the [r]remaining enemy forces[/]!':
        'The [r]Axis forces[/] arrive to gather the [r]enemy remnants[/]!',
    '[0:CHARA_G] appears on the battlefield to settle things with [1:CHARA_G]!':
        '[0:CHARA_G] arrives to settle things with [1:CHARA_G]!',
    '[0:CHARA_G] and the Royal Guard pursue [1:CHARA_G] from outside [g]Palau[/]!':
        '[0:CHARA_G] and the Royal Guard chase [1:CHARA_G]!',
    '[r]Federation reinforcements[/] advance, targeting [0:CHARA_G] and the others!':
        '[r]Federation reinforcements[/] target [0:CHARA_G]!',
    '[0:MS_G] has activated the [g]NT-D[/]! Its combat power has risen!':
        '[0:MS_G] activated the [g]NT-D[/]! Its power rises!',
    'The [r]enemy[/] special forces are nearing the target point! Shoot them down!':
        '[r]Enemy[/] special forces near the target! Down them!',
    '[0:MS_G] has been sunk! [1:MS_G] is badly damaged!':
        '[0:MS_G] sunk! [1:MS_G] badly damaged!',
    'With [0:MS_G] badly damaged, they withdraw to [1:MS_G]!':
        '[0:MS_G] badly hit! They fall back to [1:MS_G]!',
    'The [b]Federation Forces[/] and the [r]remaining Sleeves[/] withdraw from the battlefield!':
        'The [b]Federation[/] and [r]remaining Sleeves[/] withdraw!',
    'The [r]enemy[/] attack force has appeared again! It advances on [g]Neo GENESIS[/]!':
        '[r]Enemy[/] attackers again! They advance on [g]Neo GENESIS[/]!',
    'Destroy [0:CHARA_G] and the others and open the way to [2:FLD]!':
        'Destroy [0:CHARA_G] and open the way to [2:FLD]!',
    '[0:CHARA_G] has appeared to buy time until [2:FLD_PRE] is captured!':
        '[0:CHARA_G] stalls until [2:FLD_PRE] falls!',
    '[0:MS_G] and [1:MS_G] advance toward each other!':
        '[0:MS_G] and [1:MS_G] close in!',
    '[0:CHARA_G] and [1:CHARA_G] have appeared where [b]Rey[/] and the others are!':
        '[0:CHARA_G] and [1:CHARA_G] appear near [b]Rey[/]!',
    '[g]Neo GENESIS[/] has been damaged by the attack of [0:CHARA_G] and the others!':
        '[0:CHARA_G] and others damaged [g]Neo GENESIS[/]!',
    'Hurry, destroy [0:CHARA_G] and keep them from joining [1:MS_G]!':
        'Destroy [0:CHARA_G] before they join [1:MS_G]!',
    '[0:CHARA_G] has appeared at [2:FLD] aboard [0:MS_G]!':
        '[0:CHARA_G] arrives at [2:FLD] in [0:MS_G]!',
    '[0:MS_G] was shot down, so the [g]DG Cells[/] have stopped working!':
        '[0:MS_G] down! The [g]DG Cells[/] stop working!',
    # story scenes, battle dialogue, mission descriptions
    "As you make your way through an [g]Operation[/], you'll eventually be able to change a mission's difficulty, as indicated by the number of ★. Even areas you've cleared before can feel fresh at a higher difficulty.":
        "As you progress through an [g]Operation[/], you can change a mission's difficulty (the number of ★). Cleared areas feel fresh at a higher difficulty.",
    'Dark Gundam was originally created to restore the environment. But something went wrong, and it decided that the best way to save the planet was to exterminate the cause of the pollution. Us!':
        'Dark Gundam was made to restore the environment. But something went wrong, and it decided to save the planet by exterminating the polluters. Us!',
    'If we leave any enemies behind us, we could find ourselves surrounded on both sides later. And the more we can focus their attention on us, the easier it will be for the main fleet to reach Side 3.':
        'Leave enemies behind and we could be surrounded later. And the more they focus on us, the easier it is for the main fleet to reach Side 3.',
    'In battle, people focus on results and lose sight of themselves. But even in defeat, you have shown that you remember who you are, and that you will continue to fight for your beliefs. You have proven yourself a true Gundam Fighter.':
        'In battle, people chase results and lose themselves. But even in defeat, you remember who you are and fight for your beliefs. You are a true Gundam Fighter.',
    "A martial artist's fists are tools for showing you the path you have walked... There is no truer expression of your soul! Now come! Take your fists and come at me with everything you've got!!":
        "A martial artist's fists show the path you have walked... The truest expression of your soul! Now come at me with everything you've got!!",
    "It was humanity's first war since they started migrating to space, and the first where they began using weapons known as Mobile Suits. I have invited someone from that era to come and tell us more.":
        "It was humanity's first war since moving into space, and the first fought with Mobile Suits. I have invited someone from that era to tell us more.",
    "The Federation's influence had greatly declined, leading many colonies to form their own independent governments. This era would later come to be thought of as a space age of warring states.":
        "As the Federation's influence declined, many colonies formed independent governments. This era came to be seen as a space age of warring states.",
    "That's right. The Zanscare Empire's invasion was awful, and the Federation couldn't do anything to stop it, so the civilian resistance group League Militaire ended up being the ones to fight them.":
        "That's right. The Federation couldn't stop the Zanscare Empire's awful invasion, so the civilian resistance League Militaire fought them instead.",
    "That is all the knowledge we were able to obtain about the Universal Century from the Dark History. While the Universal Century did continue on past this point, we don't know the details.":
        "That is all the Dark History told us about the Universal Century. It did go on past this point, but we don't know the details.",
    "You may be right. And there's no escaping that no matter how they dressed it up, it was still nothing more than a substitute for inter-colony war. I'm sure the people who lived on Earth were none too happy about it.":
        "You may be right. However they dressed it up, it was just a substitute for war between colonies. I'm sure the people on Earth weren't happy about it.",
    "The United Earth Sphere Alliance, an organization that had been created to resolve Earth's conflicts, grew to wield enormous power, and eventually began military intervention against the independence-seeking colonies.":
        "The United Earth Sphere Alliance, created to resolve Earth's conflicts, grew enormously powerful and began military action against colonies seeking independence.",
    "Furthermore, in this era there was a facility on the moon known as D.O.M.E. that would come to play a very important part in the war. I have heard that the moon's ruler was not exactly a gentle person?":
        "In this era, a facility on the moon called D.O.M.E. played a key part in the war. I hear the moon's ruler was not exactly a gentle person?",
    "I don't know about that... But the important thing is that we were able to cast off the illusion and build a future with our own hands... That's the most important thing Garrod and the others taught me.":
        "I don't know about that... But we cast off the illusion and built a future with our own hands... That's what Garrod and the others taught me.",
    'Eight months have passed since the war reached a stalemate. At the remote colony of Side 7, the Earth Federation Forces have been working on a new plan, codenamed Operation V, to develop new models of Mobile Suit and break the ongoing stalemate.':
        'Eight months into the stalemate, at the remote colony of Side 7, the Earth Federation Forces are developing new Mobile Suits under Operation V to break the deadlock.',
    "It had been several months since the war began with the Earth Federation. Now the Earth Federation Forces finally began a large-scale counterattack against Zeon's forces on Earth. Their first target was the vital Odessa mining region.":
        "Months into the war, the Earth Federation Forces finally began a large-scale counterattack against Zeon's forces on Earth. Their first target: the vital Odessa mining region.",
    "After fending off Zeon's fierce attack on Jaburo, the Federation proceeded to plan a full-blown counteroffensive in space. The White Base, now the 13th Autonomous Corps, was to be part of this operation.":
        "After repelling Zeon's fierce attack on Jaburo, the Federation planned a full counteroffensive in space, joined by the White Base, now the 13th Autonomous Corps.",
    "As the White Base left Side 6, it was ambushed by Conscon's mobile task force, who were under orders from Dozle Zabi. This battle was broadcast throughout all of Side 6, where Char and Lalah were watching.":
        "Leaving Side 6, the White Base was ambushed by Conscon's task force on Dozle Zabi's orders. The battle was broadcast across Side 6, where Char and Lalah watched.",
    "But despite Dozle's pleas, sufficient reinforcements from A Baoa Qu and Granada never arrived. Before the battle, Dozle visited his wife, Zenna, and his daughter, Mineva, and had them evacuate to an escape capsule.":
        "Despite Dozle's pleas, enough reinforcements from A Baoa Qu and Granada never came. Before the battle, he sent his wife Zenna and daughter Mineva away in an escape capsule.",
    "Solomon fell before the Federation's attack, giving them a strong foothold to begin an invasion of the Zeon homeland, however the price paid for that foothold was severe, and filled the hearts of the White Base's crew with grief.":
        "Solomon fell, giving the Federation a foothold to invade the Zeon homeland. But the price was severe, and it filled the White Base crew's hearts with grief.",
    "Neither the fall of Solomon nor the death of his brother rattled Gihren, who continued preparing for the decisive battle with the Federation. Seeing his son like this only served to intensify Sovereign Degwin's weariness of war.":
        "Unshaken by Solomon's fall or his brother's death, Gihren prepared for the decisive battle. Seeing his son like this only deepened Sovereign Degwin's weariness of war.",
    'Among the casualties of the enormous laser, which had been made from a repurposed colony, were General Revil of the Federation Forces and Sovereign Degwin, who had been secretly meeting to discuss a truce.':
        'The giant colony laser killed General Revil of the Federation Forces and Sovereign Degwin, who had been meeting in secret to discuss a truce.',
    'Axis, which had played the other two sides against each other for its own benefit, changed its name to Neo Zeon and invaded the Earth Sphere. Thus began a new and brutal conflict, which would come to be known as the "First Neo Zeon War."':
        'Axis, having played both sides against each other, renamed itself Neo Zeon and invaded the Earth Sphere. Thus began the brutal "First Neo Zeon War."',
    'The Nu Gundam was equipped with a psycho-frame. This psycommu-based technology made dramatic performance improvements possible, but Chan was suspicious of its mysterious origins.':
        'The Nu Gundam had a psycho-frame. This psycommu technology greatly boosted performance, but Chan was suspicious of its mysterious origins.',
    'So they came up with a desperate plan. In the event their offensive failed, they would sneak into Axis and destroy it from the inside. If this succeeded, Axis would split apart and its fragments would fly out of the Earth Sphere.':
        'So they made a desperate plan: if the offensive failed, they would sneak into Axis and blow it apart from inside, sending its fragments out of the Earth Sphere.',
    'Almost everyone believed that the Earth Forces would easily win thanks to their superior numbers. But initial predictions turned out to be far off the mark, as the fighting lasted for 11 months with no sign of letting up...':
        'Nearly everyone expected the Earth Forces to win easily with their superior numbers. They were wrong: the fighting lasted 11 months with no end in sight...',
    'Cagali agreed to accompany the Archangel, and joined them as a fighter pilot. But one day her fighter was damaged by an enemy attack, and she was forced to make an emergency landing on a deserted island.':
        'Cagali joined the Archangel as a fighter pilot. But one day an enemy attack damaged her fighter, forcing an emergency landing on a deserted island.',
    "Audrey was also rescued by the Nahel Argama. Banagher's joy at seeing her again was short lived, however, as he was taken for questioning by Commander Daguza Mackle of the Federation's ECOAS special forces team.":
        "The Nahel Argama also rescued Audrey. Banagher's joy was short-lived: he was taken for questioning by Commander Daguza Mackle of the Federation's ECOAS team.",
    'Of course! This has surpassed love and transcended hatred. This has become destiny!':
        'Of course! Beyond love, beyond hatred. This is destiny!',
    "As long as you don't lose heart, you can pick yourself up as many times as you want!":
        "If you don't lose heart, you can always get back up!",
    "I don't care about the past anymore! What matters is what happens from now and onwards!":
        "I don't care about the past! What matters is what happens from now on!",
    'The military requires disciplined soldiers, and commanders who can make accurate judgments.':
        'The military needs disciplined soldiers and commanders with sound judgment.',
    'Thank you for accepting our request. Prepare to fire! Break through the enemy line!':
        'Thanks for your help. Prepare to fire! Break the enemy line!',
    'Damage rate has exceeded maximum parameters. Only remaining option... Self-destruction.':
        'Damage beyond maximum parameters. Only option left... Self-destruct.',
    "That was some fine work out there. I'd say it's even deserving of a special reward from our company.":
        'Fine work out there. It even deserves a special reward from our company.',
    "You're the only one I can leave this to, Banagher. Trust in the inner God called possibility, and move ahead.":
        'Only you can do this, Banagher. Trust the inner God called possibility, and go.',
    'The situation is even more chaotic than I thought. Now the Freedom is battling the enemy forces.':
        "It's more chaotic than I thought. Now the Freedom is fighting the enemy.",
    "Thanks for the help. We're setting course for another battlefield. Although it's probably as tough there as it is here.":
        "Thanks for the help. We're heading to another battlefield. Probably just as tough there.",
    'I wish I could say that it was skill that got us through that, but it was probably more about the suit.':
        "I'd like to say skill got us through that, but it was probably the suit.",
    'Let the perishable perish, and let the flammable burn... Our Earth Cleansing Operation is beyond your understanding!':
        'Let the perishable perish, the flammable burn... Our Earth Cleansing Operation is beyond you!',
    'Having forgotten the meaning of battle, I feel no emotion, even while shooting an enemy right through the heart.':
        "I've forgotten why I fight. I feel nothing, even shooting an enemy through the heart.",
    "People trust in justice, and run from what they don't understand! They don't learn! They don't listen! The human race will perish, as it deserves!":
        "People cling to justice and flee the unknown! They never learn! Humanity deserves to perish!",
    "I am the product of all of this, that's how I know! Humanity will be devoured by the darkness it created!":
        'I am the product of all this, so I know! Humanity will be devoured by its own darkness!',
    'Those who have, cannot understand those who have not. Those who have not, envy those who have.':
        'The haves cannot understand the have-nots. The have-nots envy the haves.',
    "To cut the twistedness from the world, for the sake of the future. That's why Gundam and I will fight!":
        "To cut the world's distortion, for the future. That's why Gundam and I fight!",
    "Without techniques to combat enemy attacks, wouldn't you feel like death is just around the corner?":
        "Without ways to counter enemy attacks, wouldn't death feel just around the corner?",
    "That's enough for today. There's no point in wasting our resources in such a meaningless effort.":
        "That's enough for today. No point wasting resources on a meaningless effort.",
    "I used to dream about meeting a prince on a white horse. I never thought I'd end up fighting alongside one.":
        "I used to dream of a prince on a white horse. I never thought I'd fight beside one.",
    "I suppose growing bigger doesn't mean growing up. How did I get stuck with so many troublesome children...?":
        "Growing bigger isn't growing up. How did I get stuck with so many troublesome kids...?",
    "You've attained an even higher score than expected. I guess Cyber-Newtypes are vital to our capabilities.":
        'An even higher score than expected. Cyber-Newtypes really are vital to us.',
    'You are a confident person able to follow your own volition. You will take to arms when necessary, am I not right?':
        'You are confident and follow your own will. You take up arms when needed, am I right?',
    "There are no principles or honor or dignity in war! People kill, and others get killed. That's all there is to it.":
        "There's no principle, honor or dignity in war! People kill and get killed. That's all.",
    "I decided I'm going to do everything I can to help Berah. I don't care if that's self-righteous or hypocritical!":
        "I'll do all I can to help Berah. I don't care if that's self-righteous or hypocritical!",
    'He has no compunctions about destroying his enemies! Just how much misfortune is there in that machine?':
        'He destroys his enemies without a second thought! How much misery is in that machine?',
    'But when the dust settles, their noble revolution has been swallowed up by bureaucracy and mediocrity.':
        'But when the dust settles, their noble revolution is swallowed by bureaucracy and mediocrity.',
    'We were meeting with the Chairman when the attack occurred. We took a Mobile Suit, as there was no time to take refuge.':
        'We were with the Chairman when the attack came. No time to take shelter, so we took a Mobile Suit.',
    "The coordinates from the Unicorn... Isn't that the prime minister's residence? The one the terrorists destroyed way back?":
        "The Unicorn's coordinates... The old prime minister's residence, destroyed by terrorists?",
    'The One Year War changed the symbiotic relationship between the Federation and the Foundation, which held the Box.':
        'The One Year War changed the bond between the Federation and the Foundation that held the Box.',
    'Damn. Connect control module directly to quasi-cortex molecular ion pump and rebuild the NLN.':
        'Damn. Wire the control module to the quasi-cortex ion pump and rebuild the NLN.',
    'All forces, please halt your attacks immediately. What can you accomplish with this endless violence!?':
        'All forces, stop your attacks now. What can this endless violence achieve!?',
    "As if I could stay quiet while Zeon is in danger! I won't let the Federation do as it pleases any longer!":
        "I won't stay quiet while Zeon is in danger! The Federation won't do as it pleases anymore!",
    'The best way to end this battle...? Cut off their escape route, and pound them with concentrated fire!':
        'Best way to end this...? Cut off their escape and pound them with concentrated fire!',
    "Hey, don't tell me you guys are still thinking about disassembling and selling those Mobile Suits... Are you?":
        "Hey, don't tell me you still want to strip and sell those Mobile Suits... Do you?",
    'To be the strongest, to go the farthest, to climb the highest! To compete, to envy, to hate, and to devour one another!':
        'To be strongest, go farthest, climb highest! To compete, envy, hate and devour one another!',
    "People trust in justice, and run from what they don't understand! They don't learn! They don't listen! And this is the result!":
        "People cling to justice and flee the unknown! They never learn! And this is the result!",
    'Did you think this would ever change!? How long have you been fighting under the influence of that sweet poison!?':
        'Did you think this would ever change!? How long have you fought drunk on that sweet poison!?',
    "Ensign Riddhe's father is a member of the Federation Central Assembly. He's a key figure in Spacenoid policy.":
        "Ensign Riddhe's father sits in the Federation Central Assembly. He's key to Spacenoid policy.",
    'Supreme Commander Gihren himself takes charge in what is effectively the final battle with the Zeon forces. Will you be able to survive and defeat the assembled warriors of Zeon?':
        'Supreme Commander Gihren himself leads the final battle with the Zeon forces. Can you survive and defeat the assembled warriors of Zeon?',
    'Space is swirling with the intrigues of three sides. The lights of many lives have been extinguished, and Kamille carries their hopes with him as he rides through the skies. You will hear the pulse of the stars...':
        'Space swirls with the intrigues of three sides. Many lives have been lost, and Kamille carries their hopes into the skies. Hear the pulse of the stars...',
    "Under the command of his old comrade Bright, Amuro boards a Gundam to stop Char's plan to massacre the people of Earth. Now you will relive your memories of the finale.":
        "Under his old comrade Bright, Amuro boards a Gundam to stop Char's plan to massacre Earth's people. Relive your memories of the finale.",
    'The Archangel has become a sacrificial pawn in a plan to bury ZAFT and friendly forces alike. Slash through with your descending sword before countless lives are lost, Gundam!':
        'The Archangel is a pawn in a plan to bury ZAFT and allies alike. Slash through with your descending sword before countless lives are lost, Gundam!',
    'In the depths of space, the plans of ZAFT and the ambitions of the Earth forces collide. Defeat the evil minds that hope for a world of destruction and fly into the never-ending future, Gundam!':
        "In deep space, ZAFT's plans and the Earth forces' ambitions collide. Defeat those who want a world of destruction and fly into the endless future, Gundam!",
    'ZAFT announces an operation to destroy the Archangel and the Freedom, whose actions are bringing chaos to the battlefield. Bring down the angels and end the nightmare, Gundam!':
        'ZAFT moves to destroy the Archangel and the Freedom, who bring chaos to the battlefield. Bring down the angels and end the nightmare, Gundam!',
    "You're ordered to launch and head to Jaburo to deliver information about the Gundam to Federation Forces HQ. But it looks like the approaching enemies are out to stop you!":
        "You're ordered to take the Gundam's data to Federation Forces HQ in Jaburo. But approaching enemies are out to stop you!",
    "There's little time remaining, and you're still within the blast radius. You're on guard against potential ambushes, but then three shadows appear before you, reeking of evil...":
        "Time is short, and you're still in the blast radius. You're wary of ambushes, but then three shadows appear before you, reeking of evil...",
    'You arrive just in time for the battle over the Colony Laser. Fierce battles are already breaking out. You must stop the fighting, and put an end to those who created this war!':
        'You arrive just in time for the fierce battle over the Colony Laser. Stop the fighting, and end those who started this war!',
    "The junk business doesn't pay well, so of course Judau and friends are interested when Astonaige says he knows how to make some cash. But will the job really be that easy?":
        "Junk doesn't pay well, so Judau and friends listen when Astonaige knows a way to make cash. But will the job really be that easy?",
    "You've launched into space to stop ZAFT from eradicating the Newtypes, only to be visited by an unexpected guest: a machine from the old Principality of Zeon!":
        'You launch into space to stop ZAFT from wiping out the Newtypes, and meet an unexpected guest: a machine of the old Principality of Zeon!',
    "As you approach the airspace of ZAFT's Messiah fortress, you are pressured by its unexpectedly strong defense forces. But Quattro and his comrades have a plan...":
        "Nearing ZAFT's Messiah fortress, you face unexpectedly strong defenses. But Quattro and his comrades have a plan...",
    'Preparations are complete for the Gundam suppression operation. The plan is to lure them by leaking false information. Defeat the Gundams who are disrupting world peace!':
        'The Gundam suppression operation is ready: lure them in with leaked false information. Defeat the Gundams disrupting world peace!',
    "Mobile Armors are known as some of the toughest weapons around. But as they say, there's always something stronger. And now, a devil arises from the bowels of the Earth...":
        "Mobile Armors are among the toughest weapons around. But there's always something stronger. Now a devil rises from the bowels of the Earth...",
    'The Federation Forces have an overwhelming quantity of Mobile Suits, as well as those developed under Operation V. Demonstrate your skill by defeating as many as you can!':
        'The Federation Forces have countless Mobile Suits, plus those of Operation V. Show your skill by defeating as many as you can!',
    "Battle isn't just about spreading destruction. It's a way of feeling your opponent's soul, and your own. Perhaps it can even be a means for communication and understanding.":
        "Battle isn't just destruction. It lets you feel your opponent's soul, and your own. Perhaps it can even bring understanding.",
    'You are exploring the memories of the Dark History with Dianna. It seems there are some remaining questions about the Second Neo Zeon War and the events that followed...':
        'You explore the Dark History with Dianna. Some questions remain about the Second Neo Zeon War and what followed...',
    'The battle to determine the true Gundam Dynasty Warrior continues. With only one person remaining, it is time to defeat him, and show the light of the human heart!':
        'The battle for the true Gundam Dynasty Warrior goes on. Only one remains. Defeat him, and show the light of the human heart!',
}
