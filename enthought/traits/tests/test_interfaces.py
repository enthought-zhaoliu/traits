#-------------------------------------------------------------------------------
#  
#  Unit test case for testing interfaces and adaptation.
#  
#  Written by: David C. Morrill
#  
#  Date: 4/10/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Unit test case for testing interfaces and adaptation.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import unittest

from enthought.traits.api \
    import HasTraits, Interface, Adapter, Instance, Int, List, TraitError, \
           adapts, implements

#-------------------------------------------------------------------------------
#  Test 'Interface' definitions:
#-------------------------------------------------------------------------------

class IFoo ( Interface ):
    
    def get_foo ( self ):
        """ Returns the current foo. """
        
class IFooPlus ( IFoo ):
    
    def get_foo_plus ( self ):
        """ Returns even more foo. """
        
class IAverage ( Interface ):
    
    def get_average ( self ):
        """ Returns the average value for the object. """
        
class IList ( Interface ):
    
    def get_list ( self ):
        """ Returns the list value for the object. """
        
#-------------------------------------------------------------------------------
#  Test 'model' classes:  
#-------------------------------------------------------------------------------
        
class Sample ( HasTraits ):
    
    s1 = Int( 1, sample = True )
    s2 = Int( 2, sample = True )
    s3 = Int( 3, sample = True )
    i1 = Int( 4 )
    i2 = Int( 5 )
    i3 = Int( 6 )
     
class SampleList ( HasTraits ):
    
    implements( IList )
    
    data = List( Int, [ 10, 20, 30 ] )
    
    def get_list ( self ):
        return self.data
        
class SampleAverage ( HasTraits ):
    
    implements( IList, IAverage )
    
    data = List( Int, [ 100, 200, 300 ] )
    
    def get_list ( self ):
        return self.data
        
    def get_average ( self ):
        value = self.get_list()
        if len( value ) == 0:
            return 0.0
            
        average = 0.0
        for item in value:
            average += item
        return (average / len( value ))
        
class SampleBad ( HasTraits ):
    
    pass
    
#-------------------------------------------------------------------------------
#  Test interfaces class:
#-------------------------------------------------------------------------------
        
class TestInterface ( HasTraits ): 
    
    a_no      = Instance( IAverage, adapt = 'no' )
    a_yes     = Instance( IAverage, adapt = 'yes' )
    a_default = Instance( IAverage, adapt = 'default' )
    l_yes     = Instance( IList )
    f_yes     = Instance( IFoo )
    fp_yes    = Instance( IFooPlus )
        
#-------------------------------------------------------------------------------
#  Test 'adapter' definitions:  
#-------------------------------------------------------------------------------
        
class SampleListAdapter ( Adapter ):
    
    implements( IList )
    
    adaptee = Instance( Sample )
    
    def get_list ( self ):
        obj = self.adaptee
        return [ getattr( obj, name ) 
                 for name in obj.trait_names( sample = True ) ]
                
class ListAverageAdapter ( Adapter ):
    
    implements( IAverage )
    
    adaptee = Instance( IList )
    
    def get_average ( self ):
        value = self.adaptee.get_list()
        if len( value ) == 0:
            return 0.0
            
        average = 0.0
        for item in value:
            average += item
        return (average / len( value ))
                
class SampleFooAdapter ( HasTraits ):
    
    adapts( Sample, IFoo )
    
    object = Instance( Sample )
    
    def __init__ ( self, object ):
        self.object = object
    
    def get_foo ( self ):
        object = self.object
        return (object.s1 + object.s2 + object.s3)
                
class FooPlusAdapter ( object ):
    
    def __init__ ( self, obj ):
        self.obj = obj
    
    def get_foo ( self ):
        return self.obj.get_foo()
    
    def get_foo_plus ( self ):
        return (self.obj.get_foo() + 1)

adapts( FooPlusAdapter, IFoo, IFooPlus )

#-------------------------------------------------------------------------------
#  'InterfacesTest' unit test class:
#-------------------------------------------------------------------------------

class InterfacesTest ( unittest.TestCase ):
        
    #---------------------------------------------------------------------------
    #  Individual unit test methods:  
    #---------------------------------------------------------------------------
        
    def test_implements_none ( self ):
        class Test ( HasTraits ):
            implements()
        
    def test_implements_one ( self ):
        class Test ( HasTraits ):
            implements( IFoo )
        
    def test_implements_multi ( self ):
        class Test ( HasTraits ):
            implements( IFoo, IAverage, IList )
        
    def test_implements_extended ( self ):
        class Test ( HasTraits ):
            implements( IFooPlus )
                    
    def test_implements_bad ( self ):
        self.assertRaises( TraitError, self.implements_bad )
            
    def test_instance_adapt_no ( self ):
        ta = TestInterface()
        self.assertRaises( TraitError, ta.set, a_no = SampleAverage() )
        self.assertRaises( TraitError, ta.set, a_no = SampleList() )
        self.assertRaises( TraitError, ta.set, a_no = Sample() )
        self.assertRaises( TraitError, ta.set, a_no = SampleBad() )
            
    def test_instance_adapt_yes ( self ):
        ta = TestInterface()
        
        ta.a_yes = SampleAverage()
        self.assertEqual( ta.a_yes.get_average(), 200.0 )
        self.assert_( isinstance( ta.a_yes, SampleAverage ) )
        
        ta.a_yes = SampleList()
        self.assertEqual( ta.a_yes.get_average(), 20.0 )
        self.assert_( isinstance( ta.a_yes, ListAverageAdapter ) )
        
        ta.l_yes = Sample()
        result = ta.l_yes.get_list()
        self.assertEqual( len( result ), 3 )
        for n in [ 1, 2, 3 ]:
            self.assert_( n in result )
        self.assert_( isinstance( ta.l_yes, SampleListAdapter ) )
        
        ta.a_yes = Sample()
        self.assertEqual( ta.a_yes.get_average(), 2.0 )
        self.assert_( isinstance( ta.a_yes, ListAverageAdapter ) )
        
        self.assertRaises( TraitError, ta.set, a_yes = SampleBad() )
        
        ta.f_yes = Sample()
        self.assertEqual( ta.f_yes.get_foo(), 6 )
        self.assert_( isinstance( ta.f_yes, SampleFooAdapter ) )
        
        ta.fp_yes = Sample( s1 = 5, s2 = 10, s3 = 15 )
        self.assertEqual( ta.fp_yes.get_foo(), 30 )
        self.assertEqual( ta.fp_yes.get_foo_plus(), 31 )
        self.assert_( isinstance( ta.fp_yes, FooPlusAdapter ) )
            
    def test_instance_adapt_default ( self ):
        ta = TestInterface()
        
        ta.a_default = SampleAverage()
        self.assertEqual( ta.a_default.get_average(), 200.0 )
        self.assert_( isinstance( ta.a_default, SampleAverage ) )
        
        ta.a_default = SampleList()
        self.assertEqual( ta.a_default.get_average(), 20.0 )
        self.assert_( isinstance( ta.a_default, ListAverageAdapter ) )
        
        ta.a_default = Sample()
        self.assertEqual( ta.a_default.get_average(), 2.0 )
        self.assert_( isinstance( ta.a_default, ListAverageAdapter ) )
        
        ta.a_default = SampleBad()
        self.assertEqual( ta.a_default, None )

    #-- Helper Methods ---------------------------------------------------------
    
    def implements_bad ( self ):
        class Test ( HasTraits ):
            implements( Sample )
    
# Run the unit tests (if invoked from the command line):        
if __name__ == '__main__':
    unittest.main()
        