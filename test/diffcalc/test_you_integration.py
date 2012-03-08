###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

from math import pi
import inspect
from nose.tools import eq_, raises
from nose.plugins.skip import Skip, SkipTest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.gdasupport.factory import create_objects
import diffcalc.gdasupport.factory  # @UnusedImport for VERBOSE
from diffcalc.gdasupport.minigda.command import Pos, Scan
from test.tools import wrap_command_to_print_calls, mneq_

EXPECTED_OBJECTS = ['delref', 'en', 'uncon', 'showref', 'cons', 'l',
                    'hardware', 'checkub', 'listub', 'mu_par', 'saveubas',
                    'eta_par', 'ct', 'setmin', 'ub', 'setcut', 'chi', 'setlat',
                    'qaz', 'addref', 'swapref', 'newub', 'naz', 'sixc', 'nu',
                    'sim', 'diffcalcdemo', 'phi', 'psi', 'sigtau', 'wl',
                    'setmax', 'dc', 'loadub', 'beta', 'hkl', 'delta', 'alpha',
                    'nu_par', 'trialub', 'delta_par', 'h', 'k', 'phi_par',
                    'mu', 'setu', 'eta', 'editref', 'con', 'setub', 'c2th',
                    'calcub', 'chi_par', 'hklverbose']

# Placeholders for names to be added to globals (for benefit of IDE)
delref = en = uncon = showref = cons = l = hardware = checkub = listub = None
mu_par = saveubas = eta_par = ct = setmin = ub = setcut = chi = setlat = None
qaz = addref = swapref = newub = naz = sixc = nu = sim = diffcalcdemo = None
phi = psi = sigtau = wl = setmax = dc = loadub = beta = hkl = delta = None
alpha = nu_par = trialub = delta_par = h = k = phi_par = mu = setu = eta = None
editref = con = setub = c2th = calcub = chi_par = hklverbose = None


PRINT_WITH_USER_SYNTAX = True
diffcalc.gdasupport.factory.VERBOSE = False

pos = wrap_command_to_print_calls(Pos(globals()), PRINT_WITH_USER_SYNTAX)


def call_scannable(scn):
    print '\n>>> %s' % scn.name
    print scn.__str__()


class TestDiffcalcFactorySixc():
    """
    All the components used here are well tested. This integration test is
    mainly to get output for the manual, to help when tweaking the user
    interface, and to make sure it all works together.
    """

    def setup(self):
        axis_names = ('mu', 'delta', 'nu', 'eta', 'chi', 'phi')
        virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
        self.objects = create_objects(
            engine_name='you',
            geometry='sixc',
            dummy_axis_names=axis_names,
            dummy_energy_name='en',
            hklverbose_virtual_angles_to_report=virtual_angles,
            simulated_crystal_counter_name='ct'
            )
        for name, obj in self.objects.iteritems():
            if inspect.ismethod(obj):
                globals()[name] = wrap_command_to_print_calls(
                                      obj, PRINT_WITH_USER_SYNTAX)
            else:
                globals()[name] = obj

    def test_created_objects(self):
        eq_(set(self.objects.keys()), set(EXPECTED_OBJECTS))

    def test_help_visually(self):
        print "\n>>> help ub"
        help(ub)
        print "\n>>> help hkl"
        help(hkl)
        print "\n>>> help newub"
        help(newub)

    def test_axes(self):
        call_scannable(sixc)
        call_scannable(phi)

    def test_with_no_ubcalc(self):
        ub()
        showref()
        call_scannable(hkl)

    def _orient(self):
        pos(wl, 1)
        call_scannable(en)  # like typing en (or en())
        newub('test')
        setlat('cubic', 1, 1, 1, 90, 90, 90)

        c2th([1, 0, 0])
        pos(sixc, [0, 60, 0, 30, 0, 0])
        addref(1, 0, 0, 'ref1')

        c2th([0, 1, 0])
        pos(phi, 90)
        addref(0, 1, 0, 'ref2')

    def test_orientation_phase(self):
        self._orient()
        ub()
        checkub()
        showref()

        U = matrix('1 0 0; 0 1 0; 0 0 1')
        UB = U * 2 * pi
        mneq_(dc.ub._ubcalc.U, U)
        mneq_(dc.ub._ubcalc.UB, UB)

    def test_hkl_read(self):
        self._orient()
        call_scannable(hkl)

    def test_help_cons(self):
        help(cons)

    def test_constraint_mgmt(self):
        diffcalc.util.DEBUG = True
        cons()  # TODO: show constrained values underneath

    def test_hkl_move_no_constraints(self):
        raise SkipTest()
        self._orient()
        pos(hkl, [1, 0, 0])

    def test_hkl_move_no_values(self):
        raise SkipTest()
        self._orient()
        con(mu)
        con(nu)
        con('a_eq_b')
        con('a_eq_b')
        pos(hkl, [1, 0, 0])

    def test_hkl_move_okay(self):
        self._orient()
        con(mu)
        con(nu)
        con('a_eq_b')
        pos(mu_par, 0)
        pos(nu_par, 0)  # TODO: Fails with qaz=90
        pos(hkl, [1, 1, 0])  # TODO: prints DEGENERATE. necessary?
        call_scannable(sixc)

    @raises(TypeError)
    def test_usage_error_signature(self):
        c2th('wrong arg', 'wrong arg')

    @raises(TypeError)
    def test_usage_error_inside(self):
        setlat('wrong arg', 'wrong arg')


# TODO: 'cons mu 2'   should work ?
# TODO:  'cons nu a_eq_b mu' should work
# TODO: Fix ' pos <h|k|l> val                 move h, k or l to val' doc string
# TODO: look at all commands together (showref, listub, cons)
# TODO: startup should sy to 'help ub' and 'help hkl'
# TODO: overide help command. Perhaps just print __doc__ if it starts
#       with '!' or '@command'
# TODO: error handling in wrapper. check TypeError depth. Give help inside
#       exception string.
# TODO: parameter scannables should return current virtual angle
#       __str__ would also show requestd

# TODO: remove need for axis_par scannables - set value, consider e.g. mu scan,
#       and moved from epics. mu scan requires mu to be same level as hkl
#       to work efficiently

# TODO: indicate in cons and after change if the mode is complete
# TODO: indicate in cons and after change if the mode is available
# TODO: 'con mu, nu, a_eq_b'
# TODO: add valueless strings to namespace

# TODO: implement mu_eq_nu mode
# TODO: add eta_half_delta and mu_half_nu modes

# TODO: provide fivec etc plugins (i13 first)
# TODO: provide arbitrary virtual names (and check arbitray motor names work)
# TODO: provide short cut mode access my number (beamline specific)

# TODO: remove sigma and tau with you engine
# TODO: handle eV / keV properly (wavelength internally, flag to energy_unit
#       equal 'keV' (default) or 'eV'

# TODO: gdasupport --> gda (check in gda first, relative path problem possible)
# TODO: Fix .__doc__ help on hkl (metaclass syetm fails under Jython with a java base class)