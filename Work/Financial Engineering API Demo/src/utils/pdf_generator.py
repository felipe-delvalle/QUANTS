"""
PDF Report Generator
Generates PDF reports from analysis data
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not available. PDF generation will not work.")


class PDFGenerator:
    """Generate PDF reports from analysis data"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize PDF generator
        
        Args:
            output_dir: Directory to save PDF files
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install with: pip install reportlab"
            )
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#16213e'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#0f3460'),
            spaceAfter=6
        ))
    
    def generate_report(self, symbol: str, analysis: Dict[str, Any]) -> str:
        """
        Generate PDF report for a symbol
        
        Args:
            symbol: Stock symbol
            analysis: Analysis data dictionary
            
        Returns:
            Path to generated PDF file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_analysis_report_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content)
        story = []
        
        # Title
        story.append(Paragraph(f"Analysis Report: {symbol}", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        if 'recommendation' in analysis:
            story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
            rec = analysis['recommendation']
            
            rec_data = [
                ['Recommendation', rec.get('recommendation', 'N/A')],
                ['Action', rec.get('action', 'N/A')],
                ['Confidence', f"{rec.get('confidence', 0) * 100:.1f}%"],
                ['Entry Range', rec.get('entry_range', 'N/A')],
                ['Stop Loss', rec.get('stop_loss', 'N/A')],
            ]
            
            if 'targets' in rec and rec['targets']:
                rec_data.append(['Targets', ', '.join(str(t) for t in rec['targets'][:3])])
            
            rec_table = Table(rec_data, colWidths=[2*inch, 4*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f3460')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
            ]))
            story.append(rec_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Technical Analysis
        if 'technical_analysis' in analysis:
            story.append(PageBreak())
            story.append(Paragraph("Technical Analysis", self.styles['CustomHeading']))
            tech = analysis['technical_analysis']
            
            if 'indicators' in tech:
                indicators = tech['indicators']
                tech_data = []
                
                if 'rsi' in indicators:
                    rsi = indicators['rsi']
                    tech_data.append(['RSI (14)', f"{rsi.get('value', 'N/A')} - {rsi.get('signal', 'N/A')}"])
                
                if 'macd' in indicators:
                    macd = indicators['macd']
                    tech_data.append(['MACD', macd.get('signal', 'N/A')])
                
                if tech_data:
                    tech_table = Table(tech_data, colWidths=[2*inch, 4*inch])
                    tech_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f3460')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
                    ]))
                    story.append(tech_table)
                    story.append(Spacer(1, 0.2*inch))
        
        # Risk Analysis
        if 'risk_analysis' in analysis:
            story.append(PageBreak())
            story.append(Paragraph("Risk Analysis", self.styles['CustomHeading']))
            risk = analysis['risk_analysis']
            
            risk_data = [
                ['Risk Score', f"{risk.get('risk_score', 0) * 10:.1f}/10"],
                ['Risk Rating', risk.get('risk_rating', 'N/A')],
            ]
            
            if 'volatility' in risk:
                vol = risk['volatility']
                risk_data.append(['Annual Volatility', f"{vol.get('annual', 0) * 100:.1f}%"])
            
            if 'max_drawdown' in risk:
                risk_data.append(['Max Drawdown', f"{risk.get('max_drawdown', 0) * 100:.1f}%"])
            
            if 'sharpe_ratio' in risk:
                risk_data.append(['Sharpe Ratio', f"{risk.get('sharpe_ratio', 0):.2f}"])
            
            risk_table = Table(risk_data, colWidths=[2*inch, 4*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f3460')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
            ]))
            story.append(risk_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report generated: {filepath}")
        return str(filepath)

