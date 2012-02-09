# TODO: class largely copied from test_calcyou
from diffcalc.geometry.plugin import DiffractometerGeometryPlugin
from diffcalc.hkl.you.position import YouPosition as Pos, YouPosition
from diffcalc.tools import assert_array_almost_equal, \
    assert_second_dict_almost_in_first, matrixeq_
from diffcalc.ub.calculation import UBCalculation
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.utils import DiffcalcException
from math import pi
from mock import Mock
from nose.plugins.skip import SkipTest
from nose.tools import raises
from tests.diffcalc.hardware.test_plugin import SimpleHardwareMonitorPlugin
from tests.diffcalc.hkl.vlieg.test_calcvlieg import createMockUbcalc, \
    createMockDiffractometerGeometry
from diffcalc.hkl.you.calcyou import YouHklCalculator
from tests.diffcalc.hkl.you.test_calcyou import _BaseTest
from diffcalc.hkl.willmott.calcwill_horizontal import WillmottHorizontalPosition
from diffcalc.hkl.you.ubcalcstrategy import YouUbCalcStrategy
from diffcalc.geometry.sixc import SixCircleYouGeometry

try:
    from Jama import Matrix
except ImportError:
    from diffcalc.npadaptor import Matrix

TORAD = pi / 180
TODEG = 180 / pi

I = Matrix.identity(3, 3)

class SkipTestSurfaceNormalVerticalCubic(_BaseTest):

    def setup(self):
        
        _BaseTest.setup(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu':-pi/2, 'eta':0}
        self.wavelength = 1
        self.UB = I.times(2 * pi)

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        if pos is not None:
            self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)


    def testHkl001(self):
        self._check((0, 0, 1),
                    Pos(mu=-90, delta=60, nu=0, eta=0, chi=90+30, phi=-90),
                    {'alpha': 30, 'beta': 30})

    def testHkl011(self):
        # raise SkipTest()
        # skipped because we can't calculate values to check against by hand
        self._check((0, 1, 1),
                    Pos(mu=-90, delta=90, nu=0, eta=0, chi=90+90, phi=-90),
#                    Pos(delta=90, gamma=0, omegah=90, phi=0),
                    {'alpha': 45, 'beta': 45})

    def testHkl010fails(self):
        self._check((0, 1, 0),
                    None,
                    {'alpha': 30, 'beta': 30}, fails=True)

    def testHkl100fails(self):
        self._check((1, 0, 0),
                    None,
                    {'alpha': 30, 'beta': 30}, fails=True)

    def testHkl111(self):
        raise SkipTest()
        # skipped because we can't calculate values to check against by hand
        self._check((1, 1, 1),
                    Pos(mu=-90, delta=90, nu=0, eta=0, chi=90+90, phi=-90),
#                    Pos(delta=90, gamma=0, omegah=90, phi=0),
                    {'alpha': 45, 'beta': 45})
#
# Willmott  You      
#           mu  = -90
# delta     delta = delta_w
# nu        nu = gamma_w
# eta       eta = 0
#           chi = 90 + omegah_w
# phi       phi = - 90 - phi_w  
   
#def willmott_to_you(pos):
#    return YouPosition(mu=-90,
#                       delta = pos.delta,
#                       nu = pos.gamma,
#                       eta = 0,
#                       chi = 90 + pos.omegah,
#                       phi = -90 - pos.phi)


# Primary and secondary reflections found with the help of DDIF on Diamond's
# i07 on Jan 27 2010


HKL0 = 2, 19, 32
REF0 = WillmottHorizontalPosition(delta=21.975, gamma=4.419, omegah=2,
                                  phi=326.2)

HKL1 = 0, 7, 22
REF1 = WillmottHorizontalPosition(delta=11.292, gamma=2.844, omegah=2,
                                  phi=124.1)

WAVELENGTH = 0.6358
ENERGY = 12.39842 / WAVELENGTH


# This is the version that Diffcalc comes up with ( see following test)
U_DIFFCALC = Matrix([[-0.7178876, 0.6643924, -0.2078944],
                     [-0.6559596, -0.5455572, 0.5216170],
                     [0.2331402, 0.5108327, 0.8274634]])


#class WillmottHorizontalGeometry(DiffractometerGeometryPlugin):
#
#    def __init__(self):
#        DiffractometerGeometryPlugin.__init__(self,
#                    name='willmott_horizontal',
#                    supportedModeGroupList=[],
#                    fixedParameterDict={},
#                    gammaLocation='base'
#                    )
#
#    def physicalAnglesToInternalPosition(self, physicalAngles):
#        assert (len(physicalAngles) == 4), "Wrong length of input list"
#        return WillmottHorizontalPosition(*physicalAngles)
#
#    def internalPositionToPhysicalAngles(self, internalPosition):
#        return internalPosition.totuple()

def willmott_to_you_fixed_mu_eta(pos):
    return YouPosition(mu=-90,
                       delta = pos.delta,
                       nu = pos.gamma,
                       eta = 0,
                       chi = 90 + pos.omegah,
                       phi = -90 - pos.phi)

class TestUBCalculationWithWillmotStrategy_Si_5_5_12_FixedMuEta():

    def setUp(self):
        
        hardware = Mock()
        hardware.getPhysicalAngleNames.return_value = ('m', 'd', 'n', 'e', 'c', 'p')
        self.ubcalc = UBCalculation(hardware, SixCircleYouGeometry(),
                                    UbCalculationNonPersister(),
                                    YouUbCalcStrategy())

    def testAgainstResultsFromJan_27_2010(self):
        self.ubcalc.newCalculation('test')
        self.ubcalc.setLattice('Si_5_5_12', 7.68, 53.48, 75.63, 90, 90, 90)
        self.ubcalc.addReflection(HKL0[0], HKL0[1], HKL0[2], willmott_to_you_fixed_mu_eta(REF0), ENERGY,
                                  'ref0', None)
        self.ubcalc.addReflection(HKL1[0], HKL1[1], HKL1[2], willmott_to_you_fixed_mu_eta(REF1), ENERGY,
                                  'ref1', None)
        self.ubcalc.calculateUB()
        print "U: ", self.ubcalc.getUMatrix()
        print "UB: ", self.ubcalc.getUBMatrix()
        matrixeq_(self.ubcalc.getUMatrix(), U_DIFFCALC)


class TestFixedMuEta(_BaseTest):

    def setup(self):
        _BaseTest.setup(self)
        self._configure_constraints()
#        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu':-pi/2, 'eta':0}
        self.wavelength = 0.6358
        B = CrystalUnderTest('xtal', 7.68, 53.48,
                             75.63, 90, 90, 90).getBMatrix()
        self.UB = U_DIFFCALC.times(B)
        self._configure_limits()


    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu':-pi/2, 'eta':0}
    
    def _configure_limits(self):
        self.mock_hardware.setLowerLimit('nu', None) # XXX
        #self.mock_hardware.setLowerLimit('delta', None)
        self.mock_hardware.setUpperLimit('delta', 90)
        self.mock_hardware.setLowerLimit('mu', None)
        self.mock_hardware.setLowerLimit('eta', None)
        self.mock_hardware.setLowerLimit('chi', None)
    
    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_eta(willmott_pos)

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
#        self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength,
#                                  virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)

    def testHkl_2_19_32_found_orientation_setting(self):
        '''Check that the or0 reflection maps back to the assumed hkl'''
        self.places = 2
        self._check_angles_to_hkl('', 999, 999, HKL0,
                        self._convert_willmott_pos(REF0),
                        self.wavelength, {'alpha': 2})

    def testHkl_0_7_22_found_orientation_setting(self):
        '''Check that the or1 reflection maps back to the assumed hkl'''
        self.places = 0
        self._check_angles_to_hkl('', 999, 999, HKL1,
                        self._convert_willmott_pos(REF1),
                        self.wavelength, {'alpha': 2})

    def testHkl_2_19_32_calculated_from_DDIF(self):
        raise SkipTest() # diffcalc finds a different solution (with -ve gamma)
        self.places = 3
        willpos = WillmottHorizontalPosition(delta=21.974, gamma=4.419, omegah=2, phi=-33.803)
        willpos = WillmottHorizontalPosition(delta=21.974, gamma=4.419, omegah=2, phi=-33.803)
        self._check((2, 19, 32),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_0_7_22_calculated_from_DDIF(self):
        raise SkipTest() # diffcalc finds a different solution (with -ve gamma)
        self.places = 3
        willpos = WillmottHorizontalPosition(delta=11.241801854649, gamma=-3.038407637123, omegah=2, phi=-3.436557497330)
        self._check((0, 7, 22),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_2_m5_12_calculated_from_DDIF(self):
        raise SkipTest() # diffcalc finds a different solution (with -ve gamma)
        self.places = 3
        willpos = WillmottHorizontalPosition(delta=5.224, gamma=10.415, omegah=2, phi=-1.972)
        self._check((2, -5, 12),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})
        
    def testHkl_2_19_32_calculated_predicted_with_diffcalc_and_found(self):
        willpos = WillmottHorizontalPosition(delta=21.974032376045, gamma= -4.418955754003, omegah=2, phi=  64.027358409574)
        self._check((2, 19, 32),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_0_7_22_calculated_predicted_with_diffcalc_and_found(self):
        willpos = WillmottHorizontalPosition(delta=11.241801854649, gamma=-3.038407637123, omegah=2, phi= -86.563442502670)
        self._check((0, 7, 22),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})

    def testHkl_2_m5_12_calculated_predicted_with_diffcalc_and_found(self):
        willpos = WillmottHorizontalPosition(delta=5.223972025344, gamma= -10.415435905622, omegah=2, phi= -90 - 102.995854571805)
        self._check((2, -5, 12),
                    self._convert_willmott_pos(willpos),
                    {'alpha': 2})


###############################################################################

def willmott_to_you_fixed_mu_chi(pos):
    return YouPosition(mu=-0,
                       delta = pos.delta,
                       nu = pos.gamma,
                       eta = pos.omegah,
                       chi = 90,
                       phi = - pos.phi)

class TestUBCalculationWithWillmotStrategy_Si_5_5_12_FixedMuChi():

    def setUp(self):
        
        hardware = Mock()
        hardware.getPhysicalAngleNames.return_value = ('m', 'd', 'n', 'e', 'c', 'p')
        self.ubcalc = UBCalculation(hardware, SixCircleYouGeometry(),
                                    UbCalculationNonPersister(),
                                    YouUbCalcStrategy())

    def testAgainstResultsFromJan_27_2010(self):
        self.ubcalc.newCalculation('test')
        self.ubcalc.setLattice('Si_5_5_12', 7.68, 53.48, 75.63, 90, 90, 90)
        self.ubcalc.addReflection(HKL0[0], HKL0[1], HKL0[2], willmott_to_you_fixed_mu_chi(REF0), ENERGY,
                                  'ref0', None)
        self.ubcalc.addReflection(HKL1[0], HKL1[1], HKL1[2], willmott_to_you_fixed_mu_chi(REF1), ENERGY,
                                  'ref1', None)
        self.ubcalc.calculateUB()
        print "U: ", self.ubcalc.getUMatrix()
        print "UB: ", self.ubcalc.getUBMatrix()
        matrixeq_(self.ubcalc.getUMatrix(), U_DIFFCALC)
 
        
class Test_Fixed_Mu_Chi(TestFixedMuEta):

    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu':0, 'chi':pi/2}
      
    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_chi(willmott_pos)


#===============================================================================
# 
#===============================================================================
#------------------------------------------------------------------------------ 
#===============================================================================
# 
#===============================================================================

# Primary and secondary reflections found with the help of DDIF on Diamond's
# i07 on Jan 28/29 2010


Pt531_HKL0 =  -1.000, 1.000, 6.0000
Pt531_REF0 = WillmottHorizontalPosition(delta=9.465, gamma=16.301, omegah=2,
                                  phi=307.94-360)

Pt531_HKL1 = -2.000,  -1.000,   7.0000
Pt531_REF1 = WillmottHorizontalPosition(delta=11.094, gamma=11.945, omegah=2,
                                  phi=238.991-360)
Pt531_HKL2 = 1,  1, 9
Pt531_REF2 = WillmottHorizontalPosition(delta=14.272, gamma=7.806, omegah=2,
                                  phi=22.9)
Pt531_WAVELENGTH = 0.6358

# This is U matrix displayed by DDIF
U_FROM_DDIF = Matrix([[-0.00312594,  -0.00063417,   0.99999491],
                      [0.99999229,  -0.00237817,   0.00312443],
                      [0.00237618,   0.99999697,   0.00064159]])

# This is the version that Diffcalc comes up with ( see following test)
Pt531_U_DIFFCALC = Matrix([[-0.0023763, -0.9999970, -0.0006416],
                           [ 0.9999923, -0.0023783,  0.0031244],
                           [-0.0031259, -0.0006342,  0.9999949]])


class TestUBCalculationWithYouStrategy_Pt531_FixedMuChi():

    def setUp(self):
        
        hardware = Mock()
        hardware.getPhysicalAngleNames.return_value = ('m', 'd', 'n', 'e', 'c', 'p')
        self.ubcalc = UBCalculation(hardware, SixCircleYouGeometry(),
                                    UbCalculationNonPersister(),
                                    YouUbCalcStrategy())

    def testAgainstResultsFromJan_28_2010(self):
        self.ubcalc.newCalculation('test')
        self.ubcalc.setLattice('Pt531', 6.204, 4.806, 23.215, 90, 90, 49.8)
        
        self.ubcalc.addReflection(Pt531_HKL0[0], Pt531_HKL0[1], Pt531_HKL0[2],
                                  willmott_to_you_fixed_mu_chi(Pt531_REF0), 12.39842 / Pt531_WAVELENGTH,
                                  'ref0', None)
        self.ubcalc.addReflection(Pt531_HKL1[0], Pt531_HKL1[1], Pt531_HKL1[2],
                                  willmott_to_you_fixed_mu_chi(Pt531_REF1), 12.39842 / Pt531_WAVELENGTH,
                                  'ref1', None)
        self.ubcalc.calculateUB()
        print "U: ", self.ubcalc.getUMatrix()
        print "UB: ", self.ubcalc.getUBMatrix()
        matrixeq_(self.ubcalc.getUMatrix(), Pt531_U_DIFFCALC)


class Test_Pt531_FixedMuChi(_BaseTest):

    def setup(self):
        _BaseTest.setup(self)
        self._configure_constraints()
#        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu':-pi/2, 'eta':0}
        self.wavelength = Pt531_WAVELENGTH
        B = CrystalUnderTest('Pt531', 6.204, 4.806, 23.215, 90, 90, 49.8).getBMatrix()
        self.UB = Pt531_U_DIFFCALC.times(B)
        self._configure_limits()


    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu':0, 'chi':pi/2}
    
    def _configure_limits(self):
        self.mock_hardware.setLowerLimit('nu', None) # XXX
        #self.mock_hardware.setLowerLimit('delta', None)
        self.mock_hardware.setUpperLimit('delta', 90)
        self.mock_hardware.setLowerLimit('mu', None)
        self.mock_hardware.setLowerLimit('eta', None)
        self.mock_hardware.setLowerLimit('chi', None)
    
    
      
    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_chi(willmott_pos)

    def _configure_ub(self):
        self.mock_ubcalc.getUBMatrix.return_value = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
#        self._check_angles_to_hkl('', 999, 999, hkl, pos, self.wavelength,
#                                  virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails('', 999, 999, hkl, pos,
                                            self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles('', 999, 999, hkl, pos, self.wavelength,
                                      virtual_expected)


    def testHkl_0_found_orientation_setting(self):
        '''Check that the or0 reflection maps back to the assumed hkl'''
        self.places = 1
        self._check_angles_to_hkl('', 999, 999, Pt531_HKL0,
                        self._convert_willmott_pos(Pt531_REF0),
                        self.wavelength, {'alpha': 2})

    def testHkl_1_found_orientation_setting(self):
        '''Check that the or1 reflection maps back to the assumed hkl'''
        self.places = 0
        self._check_angles_to_hkl('', 999, 999, Pt531_HKL1,
                        self._convert_willmott_pos(Pt531_REF1),
                        self.wavelength, {'alpha': 2})

    def testHkl_0_calculated_from_DDIF(self):
        self.places = 5
        self._check(Pt531_HKL0,
                    self._convert_willmott_pos(Pt531_REF0),
                    {'alpha': 2})

    def testHkl_1_calculated_from_DDIF(self):
        self.places = 5
        self._check(Pt531_HKL1,
                    self._convert_willmott_pos(Pt531_REF1),
                    {'alpha': 2})

    def testHkl_2_calculated_from_DDIF(self):
        self.places = 5
        self._check(Pt531_HKL2,
                    self._convert_willmott_pos(Pt531_REF2),
                    {'alpha': 2})

    def testHkl_2_m1_0_16(self):
        self.places = 5
        self._check((-1, 0, 16),
                    self._convert_willmott_pos(Pt531_REF2),
                    {'alpha': 2})

class Test_Pt531_Fixed_Mu_eta_(Test_Pt531_FixedMuChi):

    def _configure_constraints(self):
        self.constraints._constrained = {'alpha': 2 * TORAD, 'mu':-pi/2, 'eta':0}
    
    def _convert_willmott_pos(self, willmott_pos):
        return  willmott_to_you_fixed_mu_eta(willmott_pos)