"""
Collect world knowledge from Wikipedia intro paragraphs.

Approach:
- Curated list of important topics across domains
- Extract Wikipedia intro paragraphs (concise, factual summaries)
- Categories: Science, History, Geography, People, Technology, Culture

Target: 200k-400k tokens
"""

import requests
import re
from pathlib import Path
from typing import List, Dict
import time
from tqdm import tqdm


class WikipediaKnowledgeCollector:
    def __init__(self):
        """Initialize Wikipedia API client."""
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'KnowledgeCollector/1.0 (Educational Project)'
        })

    def get_topics(self) -> Dict[str, List[str]]:
        """
        Get comprehensive curated list of topics for general knowledge.
        Based on LLM-generated "study from Wikipedia" syllabus.
        Returns dictionary with category -> list of topics.
        """
        topics = {
            # HISTORY (~100 topics)
            'history_method': [
                'Historiography', 'Historical method', 'Primary source', 'Secondary source',
                'Bias', 'Propaganda', 'Causality', 'Periodization'
            ],

            'history_timeline': [
                'Human evolution', 'Prehistory', 'Neolithic Revolution', 'Bronze Age', 'Iron Age',
                'Classical antiquity', 'Middle Ages', 'Early modern period', 'Industrial Revolution',
                'Modern era', 'Globalization', 'Information Age'
            ],

            'history_ancient': [
                'Mesopotamia', 'Ancient Egypt', 'Indus Valley Civilisation', 'History of China',
                'Ancient India', 'Achaemenid Empire', 'Ancient Greece', 'Roman Republic',
                'Roman Empire', 'Silk Road', 'Hellenistic period'
            ],

            'history_religion': [
                'History of religion', 'Judaism', 'Christianity', 'Islam', 'Hinduism',
                'Buddhism', 'Jainism', 'Sikhism', 'Confucianism', 'Taoism',
                'Greek philosophy', 'Enlightenment'
            ],

            'history_medieval': [
                'Byzantine Empire', 'Feudalism', 'Crusades', 'Black Death', 'Islamic Golden Age',
                'Mongol Empire', 'History of Africa', 'Mali Empire', 'Songhai Empire',
                'Mesoamerica', 'Maya civilization', 'Aztec Empire', 'Inca Empire'
            ],

            'history_early_modern': [
                'Renaissance', 'Printing press', 'Age of Discovery', 'Columbian exchange',
                'Atlantic slave trade', 'Scientific Revolution', 'Protestant Reformation',
                'Thirty Years\' War', 'Absolutism (European history)'
            ],

            'history_revolutions': [
                'American Revolution', 'French Revolution', 'Haitian Revolution',
                'Nationalism', 'Liberalism', 'Conservatism', 'Socialism', 'Communism',
                'Fascism', 'Capitalism', 'Industrialization', 'Labor movement'
            ],

            'history_20th_century': [
                'World War I', 'Treaty of Versailles', 'Russian Revolution', 'Great Depression',
                'World War II', 'The Holocaust', 'United Nations', 'Cold War',
                'Nuclear weapons', 'Decolonization', 'Civil rights movement', 'European Union'
            ],

            # CIVICS & GOVERNMENT (~80 topics)
            'civics_foundations': [
                'State (polity)', 'Nation state', 'Sovereignty', 'Constitution', 'Rule of law',
                'Legislature', 'Executive (government)', 'Judiciary', 'Separation of powers',
                'Checks and balances', 'Federalism', 'Unitary state'
            ],

            'civics_democracy': [
                'Democracy', 'Representative democracy', 'Direct democracy', 'Elections',
                'Electoral system', 'First-past-the-post voting', 'Proportional representation',
                'Gerrymandering', 'Political party', 'Civil society'
            ],

            'civics_rights': [
                'Human rights', 'Civil liberties', 'Due process', 'Equality before the law',
                'Freedom of speech', 'Freedom of the press', 'Freedom of religion',
                'Privacy', 'Criminal justice', 'Presumption of innocence'
            ],

            'civics_policy': [
                'Public policy', 'Bureaucracy', 'Public administration', 'Tax',
                'Government budget', 'Welfare state', 'Public good (economics)',
                'Externality', 'Regulation', 'Corruption'
            ],

            'civics_economics': [
                'Supply and demand', 'Inflation', 'Unemployment', 'Gross domestic product',
                'Fiscal policy', 'Monetary policy', 'Central bank', 'Interest rate',
                'Trade', 'Tariff', 'Comparative advantage', 'Market failure'
            ],

            'civics_international': [
                'International relations', 'Diplomacy', 'Treaty', 'Sanctions',
                'United Nations', 'World Health Organization', 'International Monetary Fund',
                'World Bank', 'World Trade Organization', 'International law', 'Humanitarian law'
            ],

            'civics_media': [
                'Mass media', 'News media', 'Misinformation', 'Disinformation',
                'Media bias', 'Echo chamber (media)', 'Confirmation bias',
                'Logical fallacy', 'Critical thinking'
            ],

            # GEOGRAPHY (~50 topics)
            'geography_maps': [
                'Geography', 'Cartography', 'Map projection', 'Latitude', 'Longitude',
                'Geographic coordinate system', 'Time zone', 'Topographic map',
                'Geographic information system'
            ],

            'geography_physical': [
                'Plate tectonics', 'Tectonic plate', 'Earthquake', 'Volcano', 'Tsunami',
                'Mountain', 'River', 'Delta', 'Watershed', 'Desert', 'Glacier'
            ],

            'geography_climate': [
                'Weather', 'Climate', 'Climate classification', 'Ocean current',
                'El Niño–Southern Oscillation', 'Monsoon', 'Hurricane', 'Drought', 'Flood'
            ],

            'geography_human': [
                'Human geography', 'Population geography', 'Urbanization', 'Megacity',
                'Migration', 'Demographic transition', 'Cultural geography',
                'Economic geography', 'Political geography', 'Geopolitics'
            ],

            'geography_environment': [
                'Ecosystem', 'Biome', 'Biodiversity', 'Deforestation', 'Desertification',
                'Water scarcity', 'Sustainable development', 'Climate change',
                'Greenhouse gas', 'Carbon footprint'
            ],

            # SCIENCE (~100 topics)
            'science_method': [
                'Scientific method', 'Hypothesis', 'Experiment', 'Control group',
                'Observation', 'Peer review', 'Replication crisis',
                'Correlation does not imply causation', 'Uncertainty', 'Measurement'
            ],

            'science_physics': [
                'Newton\'s laws of motion', 'Force', 'Friction', 'Momentum',
                'Work (physics)', 'Energy', 'Conservation of energy', 'Power (physics)',
                'Gravity', 'Electric charge', 'Electric current', 'Voltage', 'Ohm\'s law',
                'Magnetism', 'Wave', 'Electromagnetic radiation', 'Thermodynamics'
            ],

            'science_chemistry': [
                'Atom', 'Chemical element', 'Periodic table', 'Isotope', 'Chemical bond',
                'Covalent bond', 'Ionic bond', 'Chemical reaction', 'Stoichiometry',
                'Catalysis', 'Acid', 'Base (chemistry)', 'pH', 'Solution (chemistry)',
                'Concentration', 'Redox'
            ],

            'science_biology': [
                'Cell (biology)', 'DNA', 'Gene', 'Protein', 'Enzyme', 'Mitosis', 'Meiosis',
                'Mendelian inheritance', 'Mutation', 'Evolution', 'Natural selection',
                'Microorganism', 'Virus', 'Bacteria', 'Immune system', 'Vaccine',
                'Antibiotic resistance', 'Ecosystem', 'Food chain'
            ],

            'science_earth_space': [
                'Geology', 'Rock cycle', 'Geologic time scale', 'Atmosphere of Earth',
                'Water cycle', 'Greenhouse effect', 'Solar System', 'Planet', 'Moon',
                'Eclipse', 'Star', 'Galaxy'
            ],

            'science_computing': [
                'Algorithm', 'Data structure', 'Computational complexity theory',
                'Cryptography', 'Public-key cryptography', 'Encryption', 'Internet',
                'Machine learning', 'Neural network'
            ],

            # GENERAL KNOWLEDGE (~60 topics)
            'general_logic': [
                'Logic', 'Argument', 'Deductive reasoning', 'Inductive reasoning',
                'Scientific skepticism', 'Cognitive bias', 'Logical fallacy'
            ],

            'general_math': [
                'Percentage', 'Ratio', 'Unit conversion', 'Graph of a function',
                'Statistics', 'Mean', 'Median', 'Standard deviation', 'Probability',
                'Expected value'
            ],

            'general_finance': [
                'Personal finance', 'Budget', 'Compound interest', 'Credit', 'Debt',
                'Inflation', 'Insurance', 'Fraud', 'Phishing'
            ],

            'general_health': [
                'Nutrition', 'Exercise', 'Sleep', 'Mental health', 'First aid',
                'Public health', 'Epidemiology'
            ],

            'general_culture': [
                'Literature', 'Mythology', 'Epic poetry', 'World literature',
                'Art', 'Art history', 'Music', 'Music theory', 'Architecture',
                'Theatre', 'Film'
            ],

            'general_global': [
                'Human migration', 'Democracy', 'Authoritarianism', 'War',
                'Genocide', 'Humanitarian aid', 'Climate change mitigation',
                'Renewable energy'
            ],

            # PEOPLE - INDIA (~150 personalities)
            'people_india_freedom': [
                'Mahatma Gandhi', 'Jawaharlal Nehru', 'Sardar Vallabhbhai Patel', 'Subhas Chandra Bose',
                'Bhagat Singh', 'Chandrashekhar Azad', 'Bal Gangadhar Tilak', 'Lala Lajpat Rai',
                'Bipin Chandra Pal', 'Gopal Krishna Gokhale', 'Dadabhai Naoroji', 'Sarojini Naidu',
                'Annie Besant', 'Maulana Abul Kalam Azad', 'Rabindranath Tagore', 'Bankim Chandra Chattopadhyay',
                'Sri Aurobindo', 'C. Rajagopalachari', 'Khan Abdul Ghaffar Khan', 'Rani Lakshmibai',
                'Mangal Pandey', 'Tipu Sultan', 'Shivaji', 'Maharana Pratap', 'Prithviraj Chauhan',
                'Ashoka', 'Chandragupta Maurya', 'Akbar', 'Aurangzeb', 'B. R. Ambedkar',
                'Jyotirao Phule', 'Savitribai Phule', 'Periyar E. V. Ramasamy', 'Ram Manohar Lohia',
                'Jayaprakash Narayan', 'Indira Gandhi', 'Atal Bihari Vajpayee', 'Rajiv Gandhi',
                'P. V. Narasimha Rao', 'Manmohan Singh'
            ],

            'people_india_social': [
                'Raja Ram Mohan Roy', 'Ishwar Chandra Vidyasagar', 'Swami Vivekananda', 'Ramakrishna',
                'Dayananda Saraswati', 'Syed Ahmad Khan', 'Mother Teresa', 'Vinoba Bhave',
                'Medha Patkar', 'Aruna Roy', 'Kailash Satyarthi'
            ],

            'people_india_science': [
                'Srinivasa Ramanujan', 'C. V. Raman', 'Jagadish Chandra Bose', 'Satyendra Nath Bose',
                'Meghnad Saha', 'Homi J. Bhabha', 'Vikram Sarabhai', 'A. P. J. Abdul Kalam',
                'Satish Dhawan', 'Subrahmanyan Chandrasekhar', 'Har Gobind Khorana', 'Venkatraman Ramakrishnan',
                'M. S. Swaminathan', 'Verghese Kurien', 'Birbal Sahni', 'Anil Kakodkar', 'Raghunath Mashelkar'
            ],

            'people_india_business': [
                'Jamsetji Tata', 'J. R. D. Tata', 'Ratan Tata', 'Dhirubhai Ambani',
                'Mukesh Ambani', 'Azim Premji', 'Narayana Murthy', 'Nandan Nilekani',
                'Kiran Mazumdar-Shaw', 'Shiv Nadar', 'Sunil Bharti Mittal', 'Gautam Adani',
                'Anand Mahindra'
            ],

            'people_india_arts': [
                'Premchand', 'R. K. Narayan', 'Mulk Raj Anand', 'Amrita Pritam',
                'Mahadevi Varma', 'Harivansh Rai Bachchan', 'Kalidasa', 'Tulsidas',
                'Mirza Ghalib', 'Kabir', 'Surdas', 'Lata Mangeshkar', 'A. R. Rahman',
                'Pandit Ravi Shankar', 'M. S. Subbulakshmi', 'Kishore Kumar', 'Satyajit Ray', 'Guru Dutt'
            ],

            'people_india_cinema': [
                'Raj Kapoor', 'Amitabh Bachchan', 'Shah Rukh Khan', 'Aamir Khan',
                'Salman Khan', 'Rajinikanth', 'Kamal Haasan', 'Dilip Kumar',
                'Dev Anand', 'Madhubala', 'Nargis', 'Sridevi', 'Rekha'
            ],

            'people_india_sports': [
                'Sachin Tendulkar', 'Virat Kohli', 'M. S. Dhoni', 'Kapil Dev',
                'Sunil Gavaskar', 'P. T. Usha', 'Milkha Singh', 'Neeraj Chopra',
                'Mary Kom', 'P. V. Sindhu', 'Saina Nehwal', 'Viswanathan Anand', 'Dhyan Chand'
            ],

            'people_india_spiritual': [
                'Gautama Buddha', 'Mahavira', 'Guru Nanak', 'Adi Shankaracharya',
                'Chaitanya Mahaprabhu', 'Mirabai', 'Sai Baba of Shirdi'
            ],

            # PEOPLE - GLOBAL (~150 personalities)
            'people_global_ancient': [
                'Socrates', 'Plato', 'Aristotle', 'Confucius', 'Laozi',
                'Jesus', 'Muhammad', 'Moses', 'Alexander the Great', 'Julius Caesar',
                'Augustus', 'Cleopatra'
            ],

            'people_global_science': [
                'Isaac Newton', 'Albert Einstein', 'Galileo Galilei', 'Johannes Kepler',
                'Nicolaus Copernicus', 'Michael Faraday', 'James Clerk Maxwell', 'Marie Curie',
                'Charles Darwin', 'Gregor Mendel', 'Louis Pasteur', 'Dmitri Mendeleev',
                'Nikola Tesla', 'Thomas Edison', 'Alan Turing', 'Ada Lovelace',
                'Leonardo da Vinci', 'Archimedes', 'Pythagoras', 'Euclid'
            ],

            'people_global_explorers': [
                'Christopher Columbus', 'Vasco da Gama', 'Ferdinand Magellan', 'Marco Polo',
                'James Cook', 'Ibn Battuta', 'Zheng He', 'Roald Amundsen', 'Neil Armstrong'
            ],

            'people_global_politics': [
                'George Washington', 'Abraham Lincoln', 'Thomas Jefferson', 'Napoleon Bonaparte',
                'Simon Bolivar', 'Benito Juárez', 'Mustafa Kemal Atatürk', 'Winston Churchill',
                'Franklin D. Roosevelt', 'John F. Kennedy', 'Mikhail Gorbachev', 'Nelson Mandela',
                'Martin Luther King Jr.', 'Margaret Thatcher', 'Angela Merkel'
            ],

            'people_global_wwii': [
                'Adolf Hitler', 'Joseph Stalin', 'Benito Mussolini', 'Vladimir Lenin',
                'Mao Zedong', 'Chiang Kai-shek', 'Hirohito', 'Charles de Gaulle'
            ],

            'people_global_rights': [
                'Rosa Parks', 'Malcolm X', 'Desmond Tutu', 'Susan B. Anthony',
                'Emmeline Pankhurst', 'Eleanor Roosevelt', 'Harriet Tubman', 'Frederick Douglass',
                'Cesar Chavez', 'Malala Yousafzai'
            ],

            'people_global_literature': [
                'William Shakespeare', 'Charles Dickens', 'Jane Austen', 'Mark Twain',
                'Leo Tolstoy', 'Fyodor Dostoevsky', 'Victor Hugo', 'George Orwell',
                'J. R. R. Tolkien', 'J. K. Rowling', 'Homer', 'Dante Alighieri',
                'Miguel de Cervantes', 'Gabriel García Márquez', 'Chinua Achebe'
            ],

            'people_global_arts': [
                'Michelangelo', 'Raphael', 'Vincent van Gogh', 'Pablo Picasso',
                'Claude Monet', 'Rembrandt', 'Frida Kahlo', 'Andy Warhol',
                'Ludwig van Beethoven', 'Wolfgang Amadeus Mozart', 'Johann Sebastian Bach',
                'Michael Jackson', 'Elvis Presley'
            ],

            'people_global_business': [
                'Henry Ford', 'Steve Jobs', 'Bill Gates', 'Elon Musk',
                'Jeff Bezos', 'Mark Zuckerberg', 'Warren Buffett', 'Jack Ma'
            ],

            'people_global_sports': [
                'Pelé', 'Diego Maradona', 'Lionel Messi', 'Cristiano Ronaldo',
                'Michael Jordan', 'Serena Williams', 'Muhammad Ali', 'Usain Bolt',
                'Roger Federer', 'Rafael Nadal'
            ],

            # ECONOMICS & FINANCE (~300+ topics)
            'econ_micro_supply_demand': [
                'Supply and demand', 'Market equilibrium', 'Elasticity (economics)',
                'Price elasticity of demand', 'Income elasticity of demand', 'Cross elasticity of demand',
                'Substitute good', 'Complementary good', 'Consumer surplus', 'Producer surplus',
                'Deadweight loss', 'Price floor', 'Price ceiling', 'Tax incidence', 'Subsidy'
            ],

            'econ_micro_consumer_firm': [
                'Utility', 'Marginal utility', 'Indifference curve', 'Budget constraint',
                'Opportunity cost', 'Marginal cost', 'Average cost', 'Economies of scale',
                'Economies of scope', 'Production function', 'Total factor productivity'
            ],

            'econ_micro_market_structure': [
                'Perfect competition', 'Monopoly', 'Oligopoly', 'Monopolistic competition',
                'Barrier to entry', 'Price discrimination', 'Predatory pricing', 'Cartel',
                'Antitrust', 'Network effect', 'Two-sided market', 'Platform economy'
            ],

            'econ_micro_game_theory': [
                'Game theory', 'Nash equilibrium', 'Prisoner\'s dilemma', 'Coordination game',
                'Signaling (economics)', 'Screening (economics)', 'Moral hazard', 'Adverse selection',
                'Principal–agent problem', 'Mechanism design'
            ],

            'econ_micro_market_failure': [
                'Market failure', 'Externality', 'Public good (economics)', 'Common-pool resource',
                'Tragedy of the commons', 'Information asymmetry', 'Pigouvian tax',
                'Coase theorem', 'Regulation', 'Cost–benefit analysis'
            ],

            'econ_macro_measurement': [
                'National accounts', 'Gross domestic product', 'Real versus nominal value (economics)',
                'Gross national income', 'Gross value added', 'Price index', 'Consumer price index',
                'Producer price index', 'Personal consumption expenditures price index', 'Deflator'
            ],

            'econ_macro_growth': [
                'Economic growth', 'Solow–Swan model', 'Endogenous growth theory',
                'Productivity', 'Human capital', 'Technological change', 'Demographic transition',
                'Labor force', 'Potential output'
            ],

            'econ_macro_cycles': [
                'Business cycle', 'Recession', 'Output gap', 'Aggregate demand',
                'Aggregate supply', 'Phillips curve', 'Okun\'s law', 'Stagflation',
                'Leading indicator', 'Purchasing Managers\' Index'
            ],

            'econ_macro_inflation': [
                'Inflation', 'Deflation', 'Hyperinflation', 'Wage inflation',
                'Inflation expectations', 'Unemployment', 'Natural rate of unemployment', 'NAIRU'
            ],

            'econ_money_monetary': [
                'Money', 'Money supply', 'Monetary policy', 'Interest rate',
                'Real interest rate', 'Nominal interest rate', 'Fisher equation', 'Central bank',
                'Inflation targeting', 'Taylor rule', 'Forward guidance', 'Quantitative easing',
                'Quantitative tightening', 'Liquidity trap'
            ],

            'econ_money_banking': [
                'Bank', 'Fractional-reserve banking', 'Credit (finance)', 'Bank run',
                'Deposit insurance', 'Lender of last resort', 'Interbank lending market',
                'Reserve requirement', 'Capital requirement', 'Basel Accords',
                'Financial system', 'Shadow banking system'
            ],

            'econ_money_yield': [
                'Yield curve', 'Term structure of interest rates', 'Expectations hypothesis',
                'Term premium', 'Duration (finance)', 'Convexity (finance)'
            ],

            'econ_international_trade': [
                'International trade', 'Comparative advantage', 'Absolute advantage',
                'Tariff', 'Quota', 'Trade barrier', 'Balance of trade',
                'Terms of trade', 'Trade deficit'
            ],

            'econ_international_fx': [
                'Foreign exchange market', 'Exchange rate', 'Exchange-rate regime',
                'Fixed exchange rate system', 'Floating exchange rate', 'Currency crisis',
                'Balance of payments', 'Current account', 'Capital account',
                'Impossible trinity', 'Interest rate parity', 'Covered interest arbitrage',
                'Purchasing power parity'
            ],

            'econ_public': [
                'Public economics', 'Tax', 'Progressive tax', 'Regressive tax',
                'Value-added tax', 'Corporate tax', 'Tax incidence', 'Government budget',
                'Budget deficit', 'National debt', 'Debt-to-GDP ratio', 'Fiscal policy',
                'Fiscal multiplier', 'Automatic stabilizer', 'Welfare state',
                'Public finance', 'Social security'
            ],

            'finance_valuation': [
                'Time value of money', 'Discounted cash flow', 'Net present value',
                'Internal rate of return', 'Risk premium', 'Cost of capital',
                'Weighted average cost of capital', 'Equity risk premium'
            ],

            'finance_portfolio': [
                'Modern portfolio theory', 'Efficient frontier', 'Diversification (finance)',
                'Capital asset pricing model', 'Beta (finance)', 'Alpha (finance)',
                'Arbitrage pricing theory', 'Fama–French three-factor model', 'Factor investing'
            ],

            'finance_market_efficiency': [
                'Efficient-market hypothesis', 'Behavioral finance', 'Market anomaly',
                'Momentum (finance)', 'Value investing'
            ],

            'finance_fixed_income': [
                'Bond (finance)', 'Bond valuation', 'Yield (finance)', 'Yield to maturity',
                'Credit spread', 'Interest rate risk'
            ],

            'finance_credit': [
                'Credit risk', 'Default (finance)', 'Probability of default',
                'Loss given default', 'Recovery rate', 'Credit rating', 'Credit rating agency',
                'Capital structure', 'Debt', 'Leverage (finance)', 'Bankruptcy',
                'Merton model', 'Credit default swap'
            ],

            'finance_derivatives': [
                'Derivative (finance)', 'Option (finance)', 'Futures contract',
                'Forward contract', 'Swap (finance)', 'Put–call parity', 'Black–Scholes model',
                'Implied volatility', 'Volatility', 'Greeks (finance)', 'Hedging',
                'Risk-neutral measure'
            ],

            'finance_microstructure': [
                'Market microstructure', 'Bid–ask spread', 'Liquidity', 'Limit order',
                'Market order', 'Order book', 'Slippage (finance)', 'Market impact',
                'High-frequency trading', 'Price discovery', 'Volatility clustering'
            ],

            'finance_crises': [
                'Financial crisis', 'Banking crisis', 'Debt crisis', 'Currency crisis',
                'Contagion (finance)', 'Systemic risk', 'Liquidity risk', 'Minsky moment',
                'Great Depression', '2007–2008 financial crisis', 'European debt crisis',
                'Savings and loan crisis', 'Asian financial crisis', 'Russian financial crisis (1998)'
            ],

            'econ_behavioral': [
                'Behavioral economics', 'Prospect theory', 'Loss aversion',
                'Overconfidence effect', 'Anchoring effect', 'Herd behavior',
                'Information cascade', 'Rational choice theory', 'Bounded rationality',
                'Nudge theory'
            ],

            'econ_econometrics_core': [
                'Econometrics', 'Regression analysis', 'Ordinary least squares',
                'Coefficient of determination', 'Standard error', 'Confidence interval',
                'Hypothesis testing', 'p-value', 'Statistical significance',
                'Multicollinearity', 'Heteroscedasticity', 'Autocorrelation'
            ],

            'econ_econometrics_causality': [
                'Causality', 'Omitted-variable bias', 'Endogeneity',
                'Instrumental variables estimation', 'Difference in differences',
                'Regression discontinuity design', 'Randomized controlled trial'
            ],

            'econ_econometrics_timeseries': [
                'Time series', 'Stationary process', 'Unit root', 'Autoregressive model',
                'Moving-average model', 'ARIMA model', 'Vector autoregression',
                'Cointegration', 'Granger causality', 'GARCH model'
            ],

            'econ_econometrics_validation': [
                'Backtesting', 'Overfitting', 'Cross-validation (statistics)',
                'Survivorship bias', 'Look-ahead bias', 'Data snooping',
                'Multiple comparisons problem'
            ],

            'finance_corporate': [
                'Corporate finance', 'Capital budgeting', 'Dividend policy',
                'Share repurchase', 'Agency cost', 'Mergers and acquisitions',
                'Leveraged buyout'
            ],

            'finance_accounting': [
                'Financial statement', 'Balance sheet', 'Income statement',
                'Cash flow statement', 'Accrual', 'Depreciation', 'Amortization',
                'Working capital', 'EBITDA', 'Free cash flow'
            ],

            'econ_development': [
                'Economic development', 'Human Development Index', 'Poverty',
                'Income inequality', 'Gini coefficient', 'Institutional economics',
                'Property rights', 'Rule of law', 'Corruption', 'Political economy'
            ]
        }

        return topics

    def fetch_wikipedia_intro(self, topic: str) -> str:
        """
        Fetch the intro paragraph(s) for a Wikipedia topic.
        Returns clean text or empty string if failed.
        """
        try:
            # Search for the page
            params = {
                'action': 'query',
                'format': 'json',
                'titles': topic,
                'prop': 'extracts',
                'exintro': True,  # Only intro section
                'explaintext': True,  # Plain text, no HTML
                'redirects': 1  # Follow redirects
            }

            response = self.session.get(self.api_url, params=params, timeout=10)

            # Check if we got valid response
            if response.status_code != 200:
                return ""

            try:
                data = response.json()
            except Exception:
                return ""

            if 'query' not in data or 'pages' not in data['query']:
                return ""

            # Get first page
            pages = data['query']['pages']
            page_id = list(pages.keys())[0]

            if page_id == '-1':  # Page not found
                return ""

            page = pages[page_id]
            if 'extract' not in page:
                return ""

            extract = page['extract']

            # Clean the text
            text = self.clean_text(extract)

            # Validate length (should be substantive intro)
            word_count = len(text.split())
            if word_count < 30 or word_count > 500:
                return ""

            return text

        except Exception as e:
            print(f"  Error fetching '{topic}': {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Clean Wikipedia text."""
        # Remove citations like [1], [2]
        text = re.sub(r'\[\d+\]', '', text)

        # Remove common mathematical notation artifacts
        text = re.sub(r'{\s*displaystyle[^}]*}', '', text)
        text = re.sub(r'\\[a-zA-Z]+\s*\{[^}]*\}', '', text)  # LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remaining LaTeX

        # Clean up parentheses with only whitespace
        text = re.sub(r'\(\s*\)', '', text)
        text = re.sub(r'\[\s*\]', '', text)

        # Remove extra whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'  +', ' ', text)

        # Remove "See also" and similar sections
        text = re.split(r'\n== ', text)[0]

        # Final cleanup
        text = text.replace('  ', ' ')

        return text.strip()

    def collect_all_topics(self) -> List[Dict[str, str]]:
        """
        Collect Wikipedia intros for all topics.
        Returns list of dicts with 'category', 'topic', 'text'.
        """
        topics_by_category = self.get_topics()

        all_articles = []
        total_topics = sum(len(topics) for topics in topics_by_category.values())

        print(f"Collecting Wikipedia intros for {total_topics} topics across {len(topics_by_category)} categories...")
        print()

        for category, topics in topics_by_category.items():
            print(f"Category: {category.upper()} ({len(topics)} topics)")

            category_count = 0
            for topic in tqdm(topics, desc=f"  {category}", leave=False):
                text = self.fetch_wikipedia_intro(topic)

                if text:
                    all_articles.append({
                        'category': category,
                        'topic': topic,
                        'text': text
                    })
                    category_count += 1

                time.sleep(0.1)  # Rate limiting

            print(f"  → Collected {category_count}/{len(topics)} articles")
            print()

        return all_articles

    def save_knowledge(self, articles: List[Dict[str, str]], output_file: Path):
        """Save knowledge articles to file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for article in articles:
                # Write as: [Topic]\n\nText\n\n
                f.write(f"[{article['topic']}]\n\n")
                f.write(article['text'])
                f.write('\n\n')

        print(f"✓ Saved {len(articles)} articles to {output_file}")

        # Calculate statistics
        total_words = sum(len(article['text'].split()) for article in articles)
        estimated_tokens = int(total_words * 1.3)

        print(f"✓ Total articles: {len(articles)}")
        print(f"✓ Total words: {total_words:,}")
        print(f"✓ Estimated tokens: {estimated_tokens:,}")

        # Breakdown by category
        print("\nBreakdown by category:")
        categories = {}
        for article in articles:
            cat = article['category']
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} articles")

        return estimated_tokens


def main():
    """Main collection script."""
    print("="*60)
    print("WIKIPEDIA KNOWLEDGE COLLECTION")
    print("="*60)
    print("\nCollecting intro paragraphs for curated topics")
    print("Target: 200k-400k tokens")
    print()

    # Initialize collector
    collector = WikipediaKnowledgeCollector()

    # Collect all topics
    articles = collector.collect_all_topics()

    if not articles:
        print("✗ No articles collected")
        return

    # Save to file
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "wiki_knowledge.txt"

    print("="*60)
    print("SAVING DATA")
    print("="*60)
    print()

    tokens = collector.save_knowledge(articles, output_file)

    print()
    print("="*60)
    print("COLLECTION COMPLETE")
    print("="*60)
    print(f"\n✓ Output: {output_file}")
    print(f"✓ Estimated tokens: {tokens:,}")
    print(f"✓ Target range: 200,000-400,000 tokens")

    if tokens < 200_000:
        print(f"\n⚠ Below target by {200_000 - tokens:,} tokens")
        print("  Consider adding more topics to the lists in get_topics()")
    elif tokens > 400_000:
        print(f"\n⚠ Above target by {tokens - 400_000:,} tokens")
        print("  Data will be sampled during merge to reach target ratio")
    else:
        print(f"\n✓ Within target range!")


if __name__ == "__main__":
    main()
