import pytest
from core.body_base import CelestialBody

def test_cannot_instantiate_directly():
    with pytest.raises(TypeError):
        CelestialBody(name   ="X",
                      radius =1.0,
                      color  = (1.0, 0.0, 0.0)
                      )
        
def test_concrete_subclass_works():
    class Dummy(CelestialBody):
        def update(self, dt: float) -> None:
            pass

    body = Dummy(name  = "test",
                radius = 1.0,
                color  = (1.0, 0.0, 0.0)
                )
    
    assert body.name      == "test"
    assert body.radius    == 1.0
    assert body.color     == (1.0, 0.0, 0.0)
    assert body.position  == (0.0, 0.0, 0.0)