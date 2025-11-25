#!/usr/bin/env python3
"""
Generative AI Sentiment Analysis Runner
Executes comprehensive sentiment analysis on market data and social media sources
"""

import asyncio
import logging
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from ml.generative_sentiment_analyzer import GenerativeSentimentAnalyzer
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sentiment_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SentimentAnalysisRunner:
    """Runner for generative AI sentiment analysis"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = ConfigManager(config_path)
        self.analyzer = GenerativeSentimentAnalyzer()
        self.results = {}
        
    async def analyze_symbol(self, symbol: str, hours_back: int = 24) -> Dict:
        """Analyze sentiment for a single symbol"""
        try:
            logger.info(f"Analyzing sentiment for {symbol} (last {hours_back} hours)")
            
            # Initialize analyzer
            await self.analyzer.initialize()
            
            # Generate sample content for analysis (in production, this would fetch real data)
            logger.info(f"Fetching sentiment data for {symbol}...")
            
            # Simulate fetching social media data
            twitter_data = await self.analyzer.fetch_twitter_sentiment(symbol, hours_back)
            reddit_data = await self.analyzer.fetch_reddit_sentiment(symbol, hours_back)
            news_data = await self.analyzer.fetch_news_sentiment(symbol, hours_back)
            
            # Aggregate sentiment
            aggregated_sentiment = await self.analyzer.aggregate_sentiment(
                symbol, hours_back
            )
            
            # Calculate market impact
            market_impact = await self.analyzer.calculate_market_impact(
                symbol, aggregated_sentiment
            )
            
            # Generate trading signals
            signals = await self.analyzer.generate_sentiment_signals(
                symbol, aggregated_sentiment
            )
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'hours_back': hours_back,
                'sentiment_sources': {
                    'twitter': twitter_data,
                    'reddit': reddit_data,
                    'news': news_data
                },
                'aggregated_sentiment': aggregated_sentiment,
                'market_impact': market_impact,
                'signals': signals,
                'confidence': aggregated_sentiment.get('confidence', 0.0) if aggregated_sentiment else 0.0,
                'sentiment_score': aggregated_sentiment.get('sentiment_score', 0.0) if aggregated_sentiment else 0.0,
                'sentiment_category': aggregated_sentiment.get('category', 'NEUTRAL') if aggregated_sentiment else 'NEUTRAL'
            }
            
            logger.info(f"Sentiment analysis completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def analyze_multiple_symbols(self, symbols: List[str], hours_back: int = 24) -> Dict:
        """Analyze sentiment for multiple symbols"""
        logger.info(f"Analyzing sentiment for {len(symbols)} symbols")
        
        tasks = [self.analyze_symbol(symbol, hours_back) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            'analysis_type': 'sentiment_analysis',
            'symbols': symbols,
            'hours_back': hours_back,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': self.generate_summary(results)
        }
    
    def generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary of sentiment analysis results"""
        summary = {
            'total_symbols': len(results),
            'symbols_analyzed': 0,
            'sentiment_breakdown': {
                'BULLISH': 0,
                'BEARISH': 0,
                'NEUTRAL': 0
            },
            'average_sentiment_score': 0.0,
            'average_confidence': 0.0,
            'high_confidence_symbols': 0,
            'positive_signals': 0,
            'negative_signals': 0,
            'neutral_signals': 0
        }
        
        total_sentiment_score = 0
        total_confidence = 0
        valid_results = 0
        
        for result in results:
            if 'error' in result:
                continue
            
            summary['symbols_analyzed'] += 1
            
            sentiment_category = result.get('sentiment_category', 'NEUTRAL')
            sentiment_score = result.get('sentiment_score', 0.0)
            confidence = result.get('confidence', 0.0)
            signals = result.get('signals', [])
            
            # Count sentiment categories
            if sentiment_category in summary['sentiment_breakdown']:
                summary['sentiment_breakdown'][sentiment_category] += 1
            
            # Calculate averages
            total_sentiment_score += sentiment_score
            total_confidence += confidence
            valid_results += 1
            
            # Count high confidence symbols
            if confidence >= 0.7:  # High confidence threshold
                summary['high_confidence_symbols'] += 1
            
            # Count signals
            for signal in signals:
                signal_type = signal.get('signal', 'NEUTRAL')
                if signal_type == 'BUY':
                    summary['positive_signals'] += 1
                elif signal_type == 'SELL':
                    summary['negative_signals'] += 1
                else:
                    summary['neutral_signals'] += 1
        
        if valid_results > 0:
            summary['average_sentiment_score'] = total_sentiment_score / valid_results
            summary['average_confidence'] = total_confidence / valid_results
        
        return summary
    
    async def scan_for_sentiment_opportunities(self, symbols: List[str], 
                                             min_confidence: float = 0.7,
                                             sentiment_threshold: float = 0.5) -> Dict:
        """Scan for sentiment-based trading opportunities"""
        logger.info(f"Scanning for sentiment opportunities with min confidence {min_confidence}")
        
        # Analyze all symbols
        analysis_results = await self.analyze_multiple_symbols(symbols)
        
        # Filter high-confidence opportunities
        opportunities = []
        for result in analysis_results['results']:
            if 'error' in result:
                continue
            
            confidence = result.get('confidence', 0)
            sentiment_score = result.get('sentiment_score', 0)
            sentiment_category = result.get('sentiment_category', 'NEUTRAL')
            signals = result.get('signals', [])
            
            # Check if meets criteria
            if confidence >= min_confidence and abs(sentiment_score) >= sentiment_threshold:
                opportunities.append({
                    'symbol': result['symbol'],
                    'confidence': confidence,
                    'sentiment_score': sentiment_score,
                    'sentiment_category': sentiment_category,
                    'signals': signals,
                    'market_impact': result.get('market_impact', {})
                })
        
        # Sort by confidence and sentiment strength
        opportunities.sort(key=lambda x: (x['confidence'], abs(x['sentiment_score'])), reverse=True)
        
        return {
            'scan_type': 'sentiment_opportunities',
            'min_confidence': min_confidence,
            'sentiment_threshold': sentiment_threshold,
            'total_symbols': len(symbols),
            'opportunities_found': len(opportunities),
            'timestamp': datetime.now().isoformat(),
            'top_opportunities': opportunities[:10]  # Top 10 opportunities
        }
    
    async def generate_market_sentiment_report(self, symbols: List[str], hours_back: int = 24) -> Dict:
        """Generate comprehensive market sentiment report"""
        logger.info(f"Generating market sentiment report for {len(symbols)} symbols")
        
        # Analyze all symbols
        analysis_results = await self.analyze_multiple_symbols(symbols, hours_back)
        
        # Calculate market-wide metrics
        market_metrics = self.calculate_market_metrics(analysis_results['results'])
        
        # Identify trending topics
        trending_topics = await self.identify_trending_topics(symbols, hours_back)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(analysis_results['summary'])
        
        return {
            'report_type': 'market_sentiment',
            'symbols': symbols,
            'hours_back': hours_back,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis_results,
            'market_metrics': market_metrics,
            'trending_topics': trending_topics,
            'recommendations': recommendations
        }
    
    def calculate_market_metrics(self, results: List[Dict]) -> Dict:
        """Calculate market-wide sentiment metrics"""
        metrics = {
            'market_sentiment_score': 0.0,
            'market_confidence': 0.0,
            'bullish_percentage': 0.0,
            'bearish_percentage': 0.0,
            'neutral_percentage': 0.0,
            'sentiment_divergence': 0.0
        }
        
        total_sentiment_score = 0
        total_confidence = 0
        valid_results = 0
        
        sentiment_counts = {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0}
        
        for result in results:
            if 'error' in result:
                continue
            
            sentiment_score = result.get('sentiment_score', 0.0)
            confidence = result.get('confidence', 0.0)
            sentiment_category = result.get('sentiment_category', 'NEUTRAL')
            
            total_sentiment_score += sentiment_score
            total_confidence += confidence
            valid_results += 1
            
            if sentiment_category in sentiment_counts:
                sentiment_counts[sentiment_category] += 1
        
        if valid_results > 0:
            metrics['market_sentiment_score'] = total_sentiment_score / valid_results
            metrics['market_confidence'] = total_confidence / valid_results
            
            # Calculate percentages
            total = sum(sentiment_counts.values())
            if total > 0:
                metrics['bullish_percentage'] = sentiment_counts['BULLISH'] / total * 100
                metrics['bearish_percentage'] = sentiment_counts['BEARISH'] / total * 100
                metrics['neutral_percentage'] = sentiment_counts['NEUTRAL'] / total * 100
                
                # Calculate sentiment divergence (how spread out the sentiment is)
                variance = sum((result.get('sentiment_score', 0.0) - metrics['market_sentiment_score']) ** 2 
                             for result in results if 'error' not in result) / valid_results
                metrics['sentiment_divergence'] = variance ** 0.5
        
        return metrics
    
    async def identify_trending_topics(self, symbols: List[str], hours_back: int) -> List[Dict]:
        """Identify trending topics in sentiment data"""
        # This is a simplified implementation
        # In production, this would analyze actual social media data
        trending_topics = []
        
        for symbol in symbols:
            # Simulate topic extraction
            topics = await self.analyzer.extract_topics(symbol, hours_back)
            for topic in topics:
                trending_topics.append({
                    'symbol': symbol,
                    'topic': topic['topic'],
                    'frequency': topic['frequency'],
                    'sentiment_impact': topic['sentiment_impact']
                })
        
        # Sort by frequency and sentiment impact
        trending_topics.sort(key=lambda x: (x['frequency'], abs(x['sentiment_impact'])), reverse=True)
        
        return trending_topics[:20]  # Top 20 topics
    
    def generate_recommendations(self, summary: Dict) -> List[Dict]:
        """Generate trading recommendations based on sentiment analysis"""
        recommendations = []
        
        avg_sentiment = summary.get('average_sentiment_score', 0)
        avg_confidence = summary.get('average_confidence', 0)
        bullish_pct = summary.get('sentiment_breakdown', {}).get('BULLISH', 0) / summary.get('symbols_analyzed', 1) * 100
        bearish_pct = summary.get('sentiment_breakdown', {}).get('BEARISH', 0) / summary.get('symbols_analyzed', 1) * 100
        
        # Generate market-wide recommendations
        if avg_confidence >= 0.7:
            if avg_sentiment > 0.3:
                recommendations.append({
                    'type': 'MARKET_WIDE',
                    'recommendation': 'BULLISH_BIAS',
                    'confidence': avg_confidence,
                    'reason': f"High confidence ({avg_confidence:.2%}) with bullish sentiment ({avg_sentiment:.2f})"
                })
            elif avg_sentiment < -0.3:
                recommendations.append({
                    'type': 'MARKET_WIDE',
                    'recommendation': 'BEARISH_BIAS',
                    'confidence': avg_confidence,
                    'reason': f"High confidence ({avg_confidence:.2%}) with bearish sentiment ({avg_sentiment:.2f})"
                })
            else:
                recommendations.append({
                    'type': 'MARKET_WIDE',
                    'recommendation': 'NEUTRAL_STANCE',
                    'confidence': avg_confidence,
                    'reason': f"High confidence ({avg_confidence:.2%}) but neutral sentiment ({avg_sentiment:.2f})"
                })
        
        # Generate sentiment divergence recommendations
        if abs(bullish_pct - bearish_pct) < 20:
            recommendations.append({
                'type': 'MARKET_CONDITION',
                'recommendation': 'HIGH_DIVERGENCE',
                'confidence': 0.8,
                'reason': f"Market sentiment is highly divided (Bullish: {bullish_pct:.1f}%, Bearish: {bearish_pct:.1f}%)"
            })
        
        return recommendations
    
    def save_results(self, results: Dict, filename: str = None) -> str:
        """Save analysis results to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/sentiment_analysis_{timestamp}.json"
        
        # Ensure reports directory exists
        Path('reports').mkdir(exist_ok=True)
        
        # Save results
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {filename}")
        return filename
    
    def print_results_summary(self, results: Dict):
        """Print summary of analysis results"""
        print("\n" + "="*60)
        print("SENTIMENT ANALYSIS RESULTS")
        print("="*60)
        print(f"Analysis Type: {results.get('analysis_type', 'N/A')}")
        print(f"Hours Back: {results.get('hours_back', 'N/A')}")
        print(f"Timestamp: {results.get('timestamp', 'N/A')}")
        print(f"Symbols Analyzed: {len(results.get('symbols', []))}")
        print("-"*60)
        
        # Print summary
        summary = results.get('summary', {})
        if summary:
            print(f"\n📈 SUMMARY:")
            print(f"   Symbols Analyzed: {summary.get('symbols_analyzed', 0)}")
            print(f"   Average Sentiment Score: {summary.get('average_sentiment_score', 0):.3f}")
            print(f"   Average Confidence: {summary.get('average_confidence', 0):.2%}")
            print(f"   High Confidence Symbols: {summary.get('high_confidence_symbols', 0)}")
            
            print(f"\n🔍 SENTIMENT BREAKDOWN:")
            for category, count in summary.get('sentiment_breakdown', {}).items():
                if count > 0:
                    percentage = count / summary.get('symbols_analyzed', 1) * 100
                    print(f"   {category}: {count} ({percentage:.1f}%)")
            
            print(f"\n📊 SIGNAL BREAKDOWN:")
            print(f"   Positive Signals: {summary.get('positive_signals', 0)}")
            print(f"   Negative Signals: {summary.get('negative_signals', 0)}")
            print(f"   Neutral Signals: {summary.get('neutral_signals', 0)}")
        
        # Print individual results
        for result in results.get('results', []):
            if 'error' in result:
                print(f"\n❌ {result['symbol']}: ERROR - {result['error']}")
                continue
            
            print(f"\n📊 {result['symbol']}:")
            print(f"   Sentiment Score: {result['sentiment_score']:.3f}")
            print(f"   Sentiment Category: {result['sentiment_category']}")
            print(f"   Confidence: {result['confidence']:.2%}")
            
            if result['signals']:
                for signal in result['signals']:
                    signal_type = signal.get('signal', 'N/A')
                    strength = signal.get('strength', 0)
                    print(f"   Signal: {signal_type} (Strength: {strength:.2f})")
        
        print("\n" + "="*60)
    
    async def run_analysis(self, symbols: List[str], hours_back: int = 24,
                          save_results: bool = True, min_confidence: float = 0.0,
                          generate_report: bool = False) -> Dict:
        """Run complete sentiment analysis"""
        logger.info(f"Starting sentiment analysis for {symbols} (last {hours_back} hours)")
        
        # Run analysis
        if generate_report:
            results = await self.generate_market_sentiment_report(symbols, hours_back)
        else:
            results = await self.analyze_multiple_symbols(symbols, hours_back)
        
        # Scan for opportunities if confidence threshold is set
        if min_confidence > 0:
            opportunities = await self.scan_for_sentiment_opportunities(symbols, min_confidence)
            results['opportunities'] = opportunities
        
        # Save results
        if save_results:
            filename = self.save_results(results)
            results['saved_file'] = filename
        
        # Print summary
        self.print_results_summary(results)
        
        return results

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generative AI Sentiment Analysis Runner')
    parser.add_argument('--symbols', nargs='+', 
                       default=['BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'XAUUSD', 'TSLA', 'AAPL'],
                       help='Symbols to analyze')
    parser.add_argument('--hours-back', type=int, default=24, help='Hours back to analyze')
    parser.add_argument('--confidence', type=float, default=0.7, help='Minimum confidence for opportunities')
    parser.add_argument('--scan-opportunities', action='store_true', help='Scan for sentiment opportunities')
    parser.add_argument('--generate-report', action='store_true', help='Generate comprehensive market report')
    parser.add_argument('--save', action='store_true', help='Save results to file')
    parser.add_argument('--output', help='Output filename for results')
    
    args = parser.parse_args()
    
    # Create runner
    runner = SentimentAnalysisRunner()
    
    try:
        if args.scan_opportunities:
            # Scan for opportunities
            results = await runner.scan_for_sentiment_opportunities(
                args.symbols, args.confidence
            )
            if args.save:
                filename = runner.save_results(results, args.output)
                print(f"Opportunity scan saved to: {filename}")
        
        else:
            # Run full analysis
            results = await runner.run_analysis(
                symbols=args.symbols,
                hours_back=args.hours_back,
                save_results=args.save,
                min_confidence=args.confidence,
                generate_report=args.generate_report
            )
            
            if args.save and 'saved_file' in results:
                print(f"Analysis saved to: {results['saved_file']}")
    
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Sentiment analysis stopped by user")
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        sys.exit(1)