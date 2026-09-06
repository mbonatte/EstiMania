/**
 * EstiMania Internationalization (i18n) Module
 * Supports:
 * - English ('en')
 * - Brazilian Portuguese ('pt-BR')
 */

const translations = {
    'en': {
        // Navigation & General
        'nav.createRoom': 'Create Room',
        'nav.browseRooms': 'Browse Rooms',
        'nav.aboutRules': 'About & Rules',
        'nav.hierarchy': 'Hierarchy:',
        'nav.diamonds': '♦ Gold',
        'nav.spades': '♠ Sword',
        'nav.hearts': '♥ Cups',
        'nav.clubs': '♣ Clubs',

        // Home Page
        'home.tagline': 'EstiMania: A thrilling card game of estimation. Guess rounds, calculate bets, and strategize your way to victory. Test your estimation skills and embrace the excitement of EstiMania. Ready to play? Let the games begin!',
        'home.btnCreate': 'Create a Room',
        'home.btnJoin': 'Join a Room',
        'home.btnBrowse': 'Browse Rooms',

        // Create Room Page
        'create.title': 'Create a Table',
        'create.desc': 'Host a game room to challenge friends or test against AI bots.',
        'create.nickname': 'Your Nickname',
        'create.nicknamePlaceholder': 'e.g. AceHigh',
        'create.roomName': 'Room Name / ID',
        'create.roomPlaceholder': 'e.g. ChampionsLounge',
        'create.pin': 'Private PIN',
        'create.pinOptional': '(Optional)',
        'create.pinPlaceholder': 'Leave blank for public room',
        'create.btnSubmit': 'Create & Join Table',

        // Join Room Page
        'join.title': 'Join a Table',
        'join.desc': 'Enter the room name and your nickname to take a seat.',
        'join.nickname': 'Your Nickname',
        'join.nicknamePlaceholder': 'e.g. CardShark',
        'join.roomID': 'Room Name / ID',
        'join.roomPlaceholder': 'e.g. ChampionsLounge',
        'join.pin': 'Room PIN',
        'join.pinOptional': '(If protected)',
        'join.pinPlaceholder': 'Leave blank if public',
        'join.btnSubmit': 'Join Table',

        // Browse Rooms Page
        'browse.title': 'Browse Tables',
        'browse.desc': 'Join an existing table or host your own game session.',
        'browse.btnCreate': 'Create New Table',
        'browse.refresh': 'Refresh',
        'browse.colName': 'Table Name',
        'browse.colPlayers': 'Players',
        'browse.colAction': 'Action',
        'browse.btnJoin': 'Join Table',
        'browse.noRoomsTitle': 'No Active Tables Found',
        'browse.noRoomsDesc': 'There are currently no open tables waiting for players.',
        'browse.btnHost': 'Host a New Table',

        // Game Room Topbar & HUD
        'room.badge': 'Room:',
        'room.leave': 'Leave Table',
        'room.coachOn': 'Coach: ON',
        'room.coachOff': 'Coach: OFF',
        'room.coachTitle': 'Toggle Coach Mode for tips and probabilities',
        'room.standings': 'Standings',
        'room.startMatch': 'Start Match',
        'room.waitingDeal': 'Waiting to deal...',
        'room.points': 'Points',
        'room.tableEmpty': 'Played cards will appear here',
        'room.cardsInHand': '{count} Card{s}',
        'room.tableChat': 'Table Chat',
        'room.chatPlaceholder': 'Type a message...',
        'room.send': 'Send',
        'room.showScores': 'Show Scores',
        'room.hideScores': 'Hide Scores',
        'room.showChat': 'Show Chat',
        'room.hideChat': 'Hide Chat',

        // Score Table
        'score.player': 'Player',
        'score.bid': 'Bid',
        'score.tricks': 'Tricks',

        // Game Setup Modal
        'setup.title': 'Game Settings',
        'setup.desc': 'Configure opponents and round length before dealing.',
        'setup.botsLabel': 'AI Bot Opponents',
        'setup.turnsLabel': 'Max Turns / Rounds',
        'setup.btnCancel': 'Cancel',
        'setup.btnConfirm': 'Start Match',

        // Betting Modal
        'bet.title': 'Place Your Bet',
        'bet.desc': 'Examine your hand below and current bids in the scoreboard.',
        'bet.coachTitle': 'Coach Advice',
        'bet.customLabel': 'Custom Bet Amount',
        'bet.btnConfirm': 'Confirm Bid',
        'bet.bestChip': '★ Best',
        'bet.recommendedBadge': '★ Recommended: {bet} ({prob}%)',

        // In-Game Turns & Prompts
        'turn.yourTurn': 'Your Turn! Pick a card to play',
        'turn.coachTipBadge': 'Coach Tip',
        'turn.coachPick': '★ Coach Pick',

        // Standings & Points Modal
        'standings.title': 'Overall Standings',
        'standings.desc': 'Cumulative points across all completed rounds.',
        'standings.colRank': 'Rank & Player',
        'standings.colStatus': 'Round Status',
        'standings.colPoints': 'Total Points',
        'standings.btnBack': 'Back to Table',
        'standings.empty': 'Match is starting. Points will calculate after Round 1.',
        'standings.bidWon': 'Bid: {bet} • Won: {wins}',
        'standings.you': 'You',

        // Final Score Podium
        'final.title': 'Final Standings',
        'final.rank': 'Rank',
        'final.player': 'Player',
        'final.rankPlayer': 'Rank & Player',
        'final.score': 'Score',
        'final.playAgain': 'Play Again',

        // Errors & Notifications
        'error.invalidCard': 'Card not valid!',
        'error.timeout': 'Timeout occurred while waiting for card selection',

        // Suits & Cards
        'suit.Diamonds': 'Diamonds',
        'suit.Spades': 'Spades',
        'suit.Hearts': 'Hearts',
        'suit.Clubs': 'Clubs',
        'card.Ace': 'Ace',
        'card.King': 'King',
        'card.Queen': 'Queen',
        'card.Jack': 'Jack',
        'card.of': 'of',

        // About & Rules Page
        'about.badge': 'Official Guide & Rulebook',
        'about.title': 'About EstiMania & Game Rules',
        'about.subtitle': 'Master the art of card estimation, trick management, and strategic betting.',
        'about.btnCreate': 'Host a Table',
        'about.btnBrowse': 'Browse Tables',
        
        // Overview
        'about.overviewTitle': 'The Essence of EstiMania',
        'about.overviewP1': 'EstiMania is a thrilling trick-taking card game of strategy, foresight, and risk management. Unlike traditional card games where having the biggest hand guarantees victory, in EstiMania your success depends entirely on how accurately you can forecast the number of tricks you will win in each round.',
        'about.overviewP2': 'Hit your exact estimate, and your score doubles! Miss your estimate by even a single trick, and you lose points for the discrepancy. Every card you play must be calculated to reach your target number of wins — no more, no less.',
        
        // Core Pillars
        'about.pillar1Title': 'Precision Estimation',
        'about.pillar1Desc': 'Bid the exact number of tricks you expect to win each round. Exact bids earn 2x points; zero bids grant a bonus point.',
        'about.pillar2Title': 'Suit Hierarchy',
        'about.pillar2Desc': 'Suits are strictly ranked: Diamonds beat Spades, Spades beat Hearts, Hearts beat Clubs. Aces are always the highest value.',
        'about.pillar3Title': 'Indian Poker Finale',
        'about.pillar3Desc': 'In the decisive 1-card final round, you cannot see your own card! You only see your opponents\' cards, forcing deductive estimation.',

        // Suits & Hierarchy
        'about.suitsTitle': 'Suit Hierarchy & Card Values',
        'about.suitsSubtitle': 'Suit dominance determines the winner whenever cards of different suits are played.',
        'about.suitDiamondsName': '♦ Diamonds (Gold)',
        'about.diamondsRank': 'Rank 1 • Supreme Suit',
        'about.diamondsDesc': 'Diamonds trump all other suits unconditionally. A 2 of Diamonds will defeat an Ace of Spades!',
        'about.suitSpadesName': '♠ Spades (Sword)',
        'about.spadesRank': 'Rank 2 • High Suit',
        'about.spadesDesc': 'Spades beat Hearts and Clubs. They are overcome only by Diamonds.',
        'about.suitHeartsName': '♥ Hearts (Cups)',
        'about.heartsRank': 'Rank 3 • Medium Suit',
        'about.heartsDesc': 'Hearts beat Clubs. They are overcome by Diamonds and Spades.',
        'about.suitClubsName': '♣ Clubs (Clubs)',
        'about.clubsRank': 'Rank 4 • Base Suit',
        'about.clubsDesc': 'The foundational suit. Overcome by any card of Diamonds, Spades, or Hearts.',
        'about.cardRankTitle': 'Card Rank Within the Same Suit',
        'about.cardRankSubtitle': 'When cards of the same suit compete, the standard numerical ranking applies:',
        'about.cardRankNote': 'The Ace is the undisputed highest card in its suit, outranking the King, Queen, Jack, 10, down to 2.',

        // Rules of Play
        'about.rulesTitle': 'How to Play: Step-by-Step',
        'about.rule1Title': '1. Dealing & Bidding',
        'about.rule1Desc': 'Each round begins with cards dealt to every player. After inspecting your hand, each player places a bet (from 0 up to the number of cards in hand) on how many tricks they anticipate winning.',
        'about.rule2Title': '2. Must Follow Suit',
        'about.rule2Desc': 'The player leading the trick may play any card. All other players MUST play a card of the same suit as the lead card if they have one. If a player holds no cards of that suit, they may play any card from any other suit.',
        'about.rule3Title': '3. Winning the Trick',
        'about.rule3Desc': 'The highest-ranking card (evaluating suit hierarchy first, then card value) wins the trick. The trick winner gathers the cards and leads the next trick.',
        'about.rule4Title': '4. Match Progression (1 ➔ N ➔ 1)',
        'about.rule4Desc': 'Round 1 starts with 1 card per player. Each successive round adds +1 card up to the match maximum (e.g. 5 or 10 cards), then scales back down round by round to 1 card.',

        // Scoring System
        'about.scoringTitle': 'Scoring System',
        'about.scoringSubtitle': 'Points are calculated at the end of each round based on the accuracy of your estimate:',
        'about.scoreExactTitle': 'Exact Bet (Bet > 0)',
        'about.scoreExactFormula': '+2 × Bet Points',
        'about.scoreExactDesc': 'Winning exactly what you estimated awards double points! E.g., estimating 3 and winning 3 earns +6 points.',
        'about.scoreZeroTitle': 'Zero Bet Success (Bet = 0)',
        'about.scoreZeroFormula': '+1 Bonus Point',
        'about.scoreZeroDesc': 'Successfully winning 0 tricks when bidding 0 awards 1 point, protecting you during weak hands.',
        'about.scoreMissTitle': 'Missed Estimate',
        'about.scoreMissFormula': '-|Bet - Won| Points',
        'about.scoreMissDesc': 'Over-bidding or under-bidding penalizes you by the absolute difference. E.g., betting 3 but winning 1 loses 2 points; betting 0 but winning 2 loses 2 points.',

        // The Final Round
        'about.finalTitle': 'The Blind Final Round (Indian Poker)',
        'about.finalSubtitle': 'The ultimate climax of every EstiMania match!',
        'about.finalDesc': 'In the final round, each player is dealt a single card, but you CANNOT view your own card! Instead, you hold it up facing outwards — you can see every other player\'s card, and they can see yours! Based on the cards you see on the table and your memory of previously played cards, you must deduce whether your unseen card is the highest and place your final bet.',

        // Strategies
        'about.strategyTitle': 'Tactics & Master Strategies',
        'about.strat1Title': 'Track Diamonds & Aces',
        'about.strat1Desc': 'Diamonds are invincible against other suits. If the Ace of Diamonds has already been played, the remaining Diamonds become the absolute masters of the board.',
        'about.strat2Title': 'Control Your Wins',
        'about.strat2Desc': 'Winning too many tricks is just as damaging as winning too few! Once your bet is satisfied, deliberately discard low or off-suit cards to let others take the lead.',
        'about.strat3Title': 'The Power of Zero Bids',
        'about.strat3Desc': 'When dealt middle-tier or low cards with no Diamonds, bidding zero is often the safest path to positive points (+1 pt) while opponents battle and lose points.',
        'about.strat4Title': 'Position Advantage',
        'about.strat4Desc': 'Being the last to bet gives you complete knowledge of the total table bids, revealing whether the round is over-bid (aggressive) or under-bid (safe).',

        // CTA
        'about.ctaTitle': 'Ready to Test Your Skills?',
        'about.ctaSubtitle': 'Create a room and invite friends, or test your estimation tactics against our Ultra Grandmaster AI bot.',
    },
    'pt-BR': {
        // Navegação & Geral
        'nav.createRoom': 'Criar Sala',
        'nav.browseRooms': 'Explorar Salas',
        'nav.aboutRules': 'Sobre e Regras',
        'nav.hierarchy': 'Hierarquia:',
        'nav.diamonds': '♦ Ouro',
        'nav.spades': '♠ Espadas',
        'nav.hearts': '♥ Copas',
        'nav.clubs': '♣ Paus',

        // Página Inicial
        'home.tagline': 'EstiMania: O emocionante jogo de cartas de estimativa e vazas. Preveja rodadas, calcule seus palpites e jogue estrategicamente para vencer. Teste sua precisão e sinta a adrenalina do EstiMania. Pronto para jogar? Que comecem os jogos!',
        'home.btnCreate': 'Criar uma Sala',
        'home.btnJoin': 'Entrar em uma Sala',
        'home.btnBrowse': 'Explorar Salas',

        // Criar Sala
        'create.title': 'Criar uma Mesa',
        'create.desc': 'Crie uma sala para desafiar seus amigos ou treinar contra bots de IA.',
        'create.nickname': 'Seu Apelido',
        'create.nicknamePlaceholder': 'ex: ReiDoBaralho',
        'create.roomName': 'Nome / ID da Sala',
        'create.roomPlaceholder': 'ex: MesaDosCampeoes',
        'create.pin': 'PIN Privado',
        'create.pinOptional': '(Opcional)',
        'create.pinPlaceholder': 'Deixe em branco para sala pública',
        'create.btnSubmit': 'Criar e Entrar na Mesa',

        // Entrar na Sala
        'join.title': 'Entrar em uma Mesa',
        'join.desc': 'Informe o nome da sala e seu apelido para tomar seu lugar à mesa.',
        'join.nickname': 'Seu Apelido',
        'join.nicknamePlaceholder': 'ex: JogadorTop',
        'join.roomID': 'Nome / ID da Sala',
        'join.roomPlaceholder': 'ex: MesaDosCampeoes',
        'join.pin': 'PIN da Sala',
        'join.pinOptional': '(Se for protegida)',
        'join.pinPlaceholder': 'Deixe em branco se for pública',
        'join.btnSubmit': 'Entrar na Mesa',

        // Explorar Salas
        'browse.title': 'Salas Disponíveis',
        'browse.desc': 'Entre em uma mesa aberta ou crie a sua própria sessão de jogo.',
        'browse.btnCreate': 'Criar Nova Mesa',
        'browse.refresh': 'Atualizar',
        'browse.colName': 'Nome da Mesa',
        'browse.colPlayers': 'Jogadores',
        'browse.colAction': 'Ação',
        'browse.btnJoin': 'Entrar',
        'browse.noRoomsTitle': 'Nenhuma Mesa Aberta',
        'browse.noRoomsDesc': 'No momento não há mesas aguardando jogadores.',
        'browse.btnHost': 'Criar Nova Mesa',

        // HUD e Mesa de Jogo
        'room.badge': 'Mesa:',
        'room.leave': 'Sair da Mesa',
        'room.coachOn': 'Treinador: LIG',
        'room.coachOff': 'Treinador: DESL',
        'room.coachTitle': 'Alternar Modo Treinador para dicas e probabilidades',
        'room.standings': 'Classificação',
        'room.startMatch': 'Iniciar Partida',
        'room.waitingDeal': 'Aguardando distribuição...',
        'room.points': 'Pontos',
        'room.tableEmpty': 'As cartas jogadas aparecerão aqui',
        'room.cardsInHand': '{count} Carta{s}',
        'room.tableChat': 'Chat da Mesa',
        'room.chatPlaceholder': 'Digite uma mensagem...',
        'room.send': 'Enviar',
        'room.showScores': 'Ver Placar',
        'room.hideScores': 'Ocultar Placar',
        'room.showChat': 'Ver Chat',
        'room.hideChat': 'Ocultar Chat',

        // Tabela de Placar
        'score.player': 'Jogador',
        'score.bid': 'Palpite',
        'score.tricks': 'Vazas',

        // Modal de Configuração de Jogo
        'setup.title': 'Configurações da Partida',
        'setup.desc': 'Escolha a quantidade de oponentes de IA e a duração da partida.',
        'setup.botsLabel': 'Oponentes Robôs (IA)',
        'setup.turnsLabel': 'Rodadas / Máx. de Cartas',
        'setup.btnCancel': 'Cancelar',
        'setup.btnConfirm': 'Iniciar Partida',

        // Modal de Apostas / Palpites
        'bet.title': 'Faça seu Palpite',
        'bet.desc': 'Examine sua mão abaixo e as apostas atuais no placar.',
        'bet.coachTitle': 'Dica do Treinador',
        'bet.customLabel': 'Quantidade de Vazas Apostadas',
        'bet.btnConfirm': 'Confirmar Palpite',
        'bet.bestChip': '★ Melhor',
        'bet.recommendedBadge': '★ Recomendado: {bet} ({prob}%)',

        // Turnos e Dicas
        'turn.yourTurn': 'Sua Vez! Escolha uma carta para jogar',
        'turn.coachTipBadge': 'Dica do Treinador',
        'turn.coachPick': '★ Dica do Treinador',

        // Modal de Classificação Geral
        'standings.title': 'Classificação Geral',
        'standings.desc': 'Pontuação acumulada de todas as rodadas já finalizadas.',
        'standings.colRank': 'Posição e Jogador',
        'standings.colStatus': 'Status da Rodada',
        'standings.colPoints': 'Pontuação Total',
        'standings.btnBack': 'Voltar à Mesa',
        'standings.empty': 'A partida está iniciando. Os pontos serão calculados após a Rodada 1.',
        'standings.bidWon': 'Palpite: {bet} • Venceu: {wins}',
        'standings.you': 'Você',

        // Pódio Final
        'final.title': 'Classificação Final',
        'final.rank': 'Pos.',
        'final.player': 'Jogador',
        'final.rankPlayer': 'Posição e Jogador',
        'final.score': 'Pontos',
        'final.playAgain': 'Jogar Novamente',

        // Erros e Avisos
        'error.invalidCard': 'Jogada inválida! Siga o naipe da mesa.',
        'error.timeout': 'Tempo esgotado para selecionar a carta.',

        // Naipes e Cartas
        'suit.Diamonds': 'Ouros',
        'suit.Spades': 'Espadas',
        'suit.Hearts': 'Copas',
        'suit.Clubs': 'Paus',
        'card.Ace': 'Ás',
        'card.King': 'Rei',
        'card.Queen': 'Dama',
        'card.Jack': 'Valete',
        'card.of': 'de',

        // Sobre & Regras
        'about.badge': 'Guia Oficial & Livro de Regras',
        'about.title': 'Sobre o EstiMania e Regras do Jogo',
        'about.subtitle': 'Domine a arte da estimativa, controle de vazas e apostas estratégicas.',
        'about.btnCreate': 'Criar uma Mesa',
        'about.btnBrowse': 'Explorar Mesas',

        // Visão Geral
        'about.overviewTitle': 'A Essência do EstiMania',
        'about.overviewP1': 'EstiMania é um jogo dinâmico de cartas e vazas baseado em estratégia, previsão e gerenciamento de risco. Diferente de jogos tradicionais onde a mão mais forte sempre vence, no EstiMania sua vitória depende de quão precisamente você prevê o número de vazas que irá vencer em cada rodada.',
        'about.overviewP2': 'Acerte o palpite exato e seus pontos dobram! Erre o palpite por apenas uma vaza e você perde pontos pela diferença. Cada carta jogada precisa ser calculada para atingir sua meta exata de vitórias — nem mais, nem menos.',

        // Pilares Principais
        'about.pillar1Title': 'Estimativa Precisa',
        'about.pillar1Desc': 'Aposte o número exato de vazas que pretende vencer em cada rodada. Palpites exatos dobram pontos; apostar zero e cumprir rende 1 ponto bônus.',
        'about.pillar2Title': 'Hierarquia Absoluta',
        'about.pillar2Desc': 'Os naipes têm poder absoluto: Ouro supera Espadas, Espadas supera Copas, Copas supera Paus. O Ás é sempre a carta mais alta.',
        'about.pillar3Title': 'Final Indian Poker',
        'about.pillar3Desc': 'Na rodada final de 1 carta, você não vê a sua carta! Você só enxerga as cartas dos oponentes, exigindo dedução pura.',

        // Naipes & Hierarquia
        'about.suitsTitle': 'Hierarquia de Naipes e Valores',
        'about.suitsSubtitle': 'O naipe dominante define o vencedor sempre que cartas de naipes diferentes colidem na mesa.',
        'about.suitDiamondsName': '♦ Ouro',
        'about.diamondsRank': '1º Lugar • Naipe Supremo',
        'about.diamondsDesc': 'Ouro supera todos os outros naipes incondicionalmente. Um 2 de Ouro vence até um Ás de Espadas!',
        'about.suitSpadesName': '♠ Espadas',
        'about.spadesRank': '2º Lugar • Naipe Alto',
        'about.spadesDesc': 'Espadas superam Copas e Paus. São vencidas apenas por cartas de Ouro.',
        'about.suitHeartsName': '♥ Copas',
        'about.heartsRank': '3º Lugar • Naipe Médio',
        'about.heartsDesc': 'Copas superam Paus. São vencidas por cartas de Ouro e Espadas.',
        'about.suitClubsName': '♣ Paus',
        'about.clubsRank': '4º Lugar • Naipe Base',
        'about.clubsDesc': 'O naipe base. Superado por qualquer carta de Ouro, Espadas ou Copas.',
        'about.cardRankTitle': 'Ordem de Força no Mesmo Naipe',
        'about.cardRankSubtitle': 'Quando os jogadores disputam com cartas do mesmo naipe, vale a ordem tradicional:',
        'about.cardRankNote': 'O Ás é a carta mais forte em seu naipe, superando o Rei, Dama, Valete, 10, até o 2.',

        // Regras de Jogo
        'about.rulesTitle': 'Como Jogar: Passo a Passo',
        'about.rule1Title': '1. Distribuição & Palpites',
        'about.rule1Desc': 'Cada rodada começa com cartas distribuídas a todos os jogadores. Após analisar sua mão, cada jogador faz sua aposta (de 0 até o total de cartas na mão) sobre quantas vazas planeja vencer.',
        'about.rule2Title': '2. Obrigação de Seguir o Naipe',
        'about.rule2Desc': 'O jogador que abre a vaza pode jogar qualquer carta. Todos os jogadores seguintes DEVEM jogar uma carta do mesmo naipe da carta de saída, se tiverem. Caso o jogador não possua nenhuma carta daquele naipe, fica livre para descartar qualquer carta de outro naipe.',
        'about.rule3Title': '3. Vencendo a Vaza',
        'about.rule3Desc': 'O jogador com a carta mais forte (avaliando a hierarquia de naipes primeiro, depois o valor da carta) vence a vaza. O vencedor recolhe a vaza e sai jogando na próxima.',
        'about.rule4Title': '4. Sequência da Partida (1 ➔ N ➔ 1)',
        'about.rule4Desc': 'A Rodada 1 começa com 1 carta por jogador. Cada rodada seguinte adiciona +1 carta até o limite da partida (ex: 5 ou 10 cartas), e depois diminui gradualmente de volta até 1 carta.',

        // Sistema de Pontuação
        'about.scoringTitle': 'Sistema de Pontuação',
        'about.scoringSubtitle': 'Os pontos são calculados ao término de cada rodada com base na precisão da sua aposta:',
        'about.scoreExactTitle': 'Palpite Exato (Aposta > 0)',
        'about.scoreExactFormula': '+2 × Aposta Pontos',
        'about.scoreExactDesc': 'Vencer exatamente o que apostou dobra seus pontos! Ex: apostar 3 e vencer 3 rende +6 pontos.',
        'about.scoreZeroTitle': 'Palpite Zero Correto (Aposta = 0)',
        'about.scoreZeroFormula': '+1 Ponto Bônus',
        'about.scoreZeroDesc': 'Vencer 0 vazas ao apostar 0 rende 1 ponto, protegendo você em rodadas de cartas fracas.',
        'about.scoreMissTitle': 'Palpite Errado',
        'about.scoreMissFormula': '-|Aposta - Vencidas| Pontos',
        'about.scoreMissDesc': 'Apostar a mais ou a menos penaliza você pela diferença absoluta. Ex: apostar 3 e vencer 1 desconta 2 pontos; apostar 0 e vencer 2 desconta 2 pontos.',

        // A Rodada Final
        'about.finalTitle': 'A Rodada Final Às Cegas (Indian Poker)',
        'about.finalSubtitle': 'O grande clímax decisivo de cada partida de EstiMania!',
        'about.finalDesc': 'Na rodada final, cada jogador recebe 1 carta, mas você NÃO pode olhar a sua própria carta! Em vez disso, sua carta fica virada para fora — você enxerga as cartas de todos os adversários e eles enxergam a sua! Com base nas cartas visíveis e na memória das cartas já jogadas, você deve deduzir se sua carta oculta é a vencedora e fazer sua aposta final.',

        // Estratégias
        'about.strategyTitle': 'Táticas e Dicas de Mestre',
        'about.strat1Title': 'Conte os Ouros e Ases',
        'about.strat1Desc': 'Ouros são imbatíveis contra outros naipes. Se o Ás de Ouro já foi jogado, os Ouros restantes tornam-se os donos absolutos da mesa.',
        'about.strat2Title': 'Controle Suas Vitórias',
        'about.strat2Desc': 'Vencer vazas demais é tão prejudicial quanto vencer de menos! Ao atingir sua meta, jogue cartas baixas para deixar os outros levarem.',
        'about.strat3Title': 'O Poder da Aposta Zero',
        'about.strat3Desc': 'Com cartas médias ou baixas sem Ouro, apostar zero geralmente é o caminho mais seguro para pontuar (+1 pt) enquanto adversários arriscam e perdem.',
        'about.strat4Title': 'Vantagem de Posição',
        'about.strat4Desc': 'Ser o último a apostar dá a você a visão do total de palpites na mesa, revelando se a rodada está disputada demais ou conservadora.',

        // CTA
        'about.ctaTitle': 'Pronto para Testar Suas Habilidades?',
        'about.ctaSubtitle': 'Crie uma sala e convide amigos, ou teste suas táticas de estimativa contra nosso bot Ultra Grandmaster.',
    }
};

class I18nManager {
    constructor() {
        const saved = localStorage.getItem('estimania_lang');
        if (saved && (saved === 'pt-BR' || saved === 'en')) {
            this.currentLang = saved;
        } else {
            // Auto-detect browser language
            const navLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
            this.currentLang = navLang.startsWith('pt') ? 'pt-BR' : 'en';
        }
    }

    getLanguage() {
        return this.currentLang;
    }

    setLanguage(lang) {
        if (lang !== 'en' && lang !== 'pt-BR') return;
        this.currentLang = lang;
        localStorage.setItem('estimania_lang', lang);
        document.documentElement.lang = lang === 'pt-BR' ? 'pt-BR' : 'en';
        this.applyTranslations();
        window.dispatchEvent(new CustomEvent('estimaniaLanguageChanged', { detail: { lang } }));
    }

    toggleLanguage() {
        const next = this.currentLang === 'pt-BR' ? 'en' : 'pt-BR';
        this.setLanguage(next);
        return next;
    }

    t(key, params = {}) {
        const dict = translations[this.currentLang] || translations['en'];
        let str = dict[key] || translations['en'][key] || key;
        for (const [k, v] of Object.entries(params)) {
            str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
        }
        return str;
    }

    formatCard(cardStr) {
        if (!cardStr) return '';
        // Format e.g. "1 of Diamonds" -> "Ás de Ouros" or "Ace of Diamonds"
        const parts = cardStr.split(' of ');
        if (parts.length !== 2) return cardStr;
        const [val, suit] = parts;
        
        let valName = val;
        if (val === '1') valName = this.t('card.Ace');
        else if (val === '13') valName = this.t('card.King');
        else if (val === '12') valName = this.t('card.Queen');
        else if (val === '11') valName = this.t('card.Jack');

        const suitName = this.t(`suit.${suit}`);
        const ofWord = this.t('card.of');
        return `${valName} ${ofWord} ${suitName}`;
    }

    applyTranslations(root = document) {
        const elements = root.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (key) {
                el.textContent = this.t(key);
            }
        });

        const htmlElements = root.querySelectorAll('[data-i18n-html]');
        htmlElements.forEach(el => {
            const key = el.getAttribute('data-i18n-html');
            if (key) {
                el.innerHTML = this.t(key);
            }
        });

        const placeholders = root.querySelectorAll('[data-i18n-placeholder]');
        placeholders.forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (key) {
                el.setAttribute('placeholder', this.t(key));
            }
        });

        const titles = root.querySelectorAll('[data-i18n-title]');
        titles.forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            if (key) {
                el.setAttribute('title', this.t(key));
            }
        });

        // Update language toggle button label if present
        const langLabel = document.getElementById('langToggleLabel');
        if (langLabel) {
            langLabel.textContent = this.currentLang === 'pt-BR' ? '🇧🇷 PT' : '🇺🇸 EN';
        }
    }
}

export const i18n = new I18nManager();
export default i18n;
