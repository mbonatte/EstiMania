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
